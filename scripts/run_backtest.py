"""
Script pour exécuter le backtest complet de DeepPilot.

Exécute la stratégie ML sur l'historique et sauvegarde les résultats
pour les afficher dans l'app.

Usage:
    python scripts/run_backtest.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from api.database import get_engine
from ml.config import ETF_TICKERS
from ml.portfolio.backtester import Backtester
from ml.portfolio.deeppilot_strategy import DeepPilotStrategy


def load_data_from_db(years: int = 15) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge les données depuis la base."""
    engine = get_engine()

    # Prix des ETF
    tickers = list(ETF_TICKERS) + ["QQQ"]
    tickers_str = ", ".join([f"'{t}'" for t in tickers])

    query_prices = f"""
    SELECT date, ticker, close
    FROM price
    WHERE ticker IN ({tickers_str})
    AND date >= CURRENT_DATE - INTERVAL '{years} years'
    ORDER BY date, ticker
    """

    df_prices = pd.read_sql(query_prices, engine, parse_dates=["date"])
    df_prices = df_prices.pivot(index="date", columns="ticker", values="close")

    # Données macro
    query_macro = f"""
    SELECT
        date,
        vix,
        credit_spread_hy AS credit_spread,
        yield_curve_10y2y,
        t10y,
        t3mo
    FROM macro_indicator
    WHERE date >= CURRENT_DATE - INTERVAL '{years} years'
    ORDER BY date
    """

    df_macro = pd.read_sql(query_macro, engine, parse_dates=["date"])
    df_macro = df_macro.set_index("date")

    return df_prices, df_macro


def run_deeppilot_backtest(
    df_prices: pd.DataFrame,
    df_macro: pd.DataFrame,
    start_date: str,
    end_date: str,
    train_years: int = 3,
) -> dict:
    """
    Exécute le backtest DeepPilot complet.

    Returns:
        Dict avec returns, métriques, et données cumulées
    """
    print(f"\n{'='*60}")
    print(f"BACKTEST DEEPPILOT: {start_date} -> {end_date}")
    print(f"{'='*60}\n")

    # Créer la stratégie
    strategy = DeepPilotStrategy(
        risk_free_rate=0.04,
        min_weight=0.05,
        max_weight=0.25,
        regime_adjustment=True,
    )

    # Créer le backtester
    backtester = Backtester(
        transaction_cost=0.001,  # 0.1%
        rebalance_freq="M",  # Mensuel
        risk_free_rate=0.04,
    )

    # Exécuter le backtest
    result = backtester.run(
        strategy=strategy,
        df_prices=df_prices,
        df_macro=df_macro,
        start_date=start_date,
        end_date=end_date,
        train_years=train_years,
        retrain_freq="Y",  # Réentraîner chaque année
    )

    return result


def calculate_metrics(returns: pd.Series, risk_free_rate: float = 0.04) -> dict:
    """Calcule les métriques de performance."""
    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / 252
    cagr = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0
    volatility = returns.std() * np.sqrt(252)
    sharpe = (cagr - risk_free_rate) / volatility if volatility > 0 else 0

    # Max Drawdown
    cumret = (1 + returns).cumprod()
    cummax = cumret.cummax()
    drawdown = (cumret - cummax) / cummax
    max_dd = drawdown.min()

    # Win rate
    win_rate = (returns > 0).sum() / len(returns)

    return {
        "total_return": round(total_return * 100, 2),
        "cagr": round(cagr * 100, 2),
        "volatility": round(volatility * 100, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown": round(max_dd * 100, 2),
        "win_rate": round(win_rate * 100, 1),
    }


def main():
    output_path = ROOT_DIR / "data" / "backtest_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print("Chargement des données...")
        df_prices, df_macro = load_data_from_db(years=15)

        print(f"Données prix: {df_prices.index[0]} -> {df_prices.index[-1]}")
        print(f"Données macro: {df_macro.index[0]} -> {df_macro.index[-1]}")

        # Dates de backtest
        # On utilise les 10 dernières années pour le backtest (3 ans pour training)
        end_date = df_prices.index[-1].strftime("%Y-%m-%d")
        start_date = (df_prices.index[-1] - pd.DateOffset(years=10)).strftime("%Y-%m-%d")

        print(f"\nPériode de backtest: {start_date} -> {end_date}")
        result = run_deeppilot_backtest(
            df_prices,
            df_macro,
            start_date,
            end_date,
            train_years=3,
        )

        # Calculer les métriques DeepPilot
        deeppilot_metrics = calculate_metrics(result.returns)
        deeppilot_metrics["name"] = "DeepPilot"

        print("\n" + "=" * 60)
        print("RÉSULTATS DEEPPILOT:")
        print("=" * 60)
        for key, value in deeppilot_metrics.items():
            print(f"  {key}: {value}")

        # Returns cumulés (sous-échantillonné par semaine)
        cumret = (1 + result.returns).cumprod() * 100
        cumret_weekly = cumret.resample("W").last().dropna()

        cumulative_data = [
            {"date": d.strftime("%Y-%m-%d"), "value": round(v, 2)} for d, v in cumret_weekly.items()
        ]

        # Sauvegarder les résultats
        output = {
            "metrics": deeppilot_metrics,
            "cumulative_returns": cumulative_data,
            "period": {
                "start": start_date,
                "end": end_date,
            },
            "generated_at": datetime.now().isoformat(),
        }

        output_path = ROOT_DIR / "data" / "backtest_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\nRésultats sauvegardés dans: {output_path}")

    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback

        traceback.print_exc()

        # Créer un fichier avec l'erreur pour éviter les problèmes dans l'API
        output = {
            "metrics": None,
            "cumulative_returns": [],
            "period": {"start": "unknown", "end": "unknown"},
            "error": str(e),
            "generated_at": datetime.now().isoformat(),
        }

        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        # Exit avec code 0 pour ne pas bloquer le workflow
        # L'erreur est loguée et le fichier JSON contient l'info
        print("\nFichier JSON créé avec erreur, workflow continue...")
        sys.exit(0)


if __name__ == "__main__":
    main()
