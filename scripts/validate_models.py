#!/usr/bin/env python3
"""
Script de validation des modèles ML.

Entraîne les modèles HMM et RF sur des données récentes et vérifie
que les métriques sont au-dessus des seuils minimaux.

Usage:
    python scripts/validate_models.py

Codes de sortie:
    0 : Tous les modèles sont valides
    1 : Au moins un modèle a échoué la validation
"""

import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

from mlops.config import PERFORMANCE_THRESHOLDS


def validate_hmm() -> tuple[bool, dict]:
    """
    Valide le modèle HMM de détection de régimes avec métriques économiques.

    Phase 4.5 : Utilise des métriques économiques (crisis_recall, séparation
    rendement/volatilité) au lieu du silhouette score.

    Returns:
        Tuple (success, metrics)
    """
    print("\n" + "=" * 60)
    print("VALIDATION HMM - Détection de régimes (métriques économiques)")
    print("=" * 60)

    try:
        import os
        from datetime import datetime

        from dotenv import load_dotenv
        from sqlalchemy import create_engine

        from data.extractors.extract_yfinance import ETF_TICKERS, download_etf_prices
        from ml.evaluation.regime_validation import (
            print_validation_report,
            validate_hmm_economic,
        )
        from ml.features import prepare_regime_features
        from ml.models.regime_hmm import RegimeHMM

        load_dotenv()

        # Charger les données
        print("Chargement des données...")
        prices = download_etf_prices(
            ETF_TICKERS, start_date="2008-01-01", end_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Charger macro (DB ou fichier local en fallback)
        macro_df = None
        DATABASE_URL = os.getenv("SUPABASE_DB_URL")

        if DATABASE_URL:
            try:
                from sqlalchemy import create_engine

                engine = create_engine(DATABASE_URL)
                query_macro = "SELECT date, vix, credit_spread_hy, yield_curve_10y2y FROM macro_indicator ORDER BY date"
                macro_df = pd.read_sql(query_macro, engine, parse_dates=["date"])
                macro_df = macro_df.set_index("date")
                print("Données macro chargées depuis Supabase")
            except Exception as e:
                print(f"Supabase indisponible, fallback sur fichier local: {e}")

        # Fallback sur fichier CSV local
        if macro_df is None or macro_df.empty:
            from pathlib import Path

            macro_file = Path(__file__).parent.parent / "data" / "raw" / "macro_20260515.csv"
            if macro_file.exists():
                macro_df = pd.read_csv(macro_file, parse_dates=["Date"])
                macro_df = macro_df.rename(columns={"Date": "date"})
                macro_df = macro_df.set_index("date")
                print(f"Données macro chargées depuis {macro_file}")
            else:
                print(f"ERREUR: Fichier macro introuvable: {macro_file}")
                return False, {}

        if macro_df["credit_spread_hy"].isna().any():
            macro_df["credit_spread_hy"] = macro_df["credit_spread_hy"].ffill().bfill().fillna(4.5)

        # Combiner
        combined_df = prices.join(macro_df, how="inner")

        # Préparer les features
        X = prepare_regime_features(combined_df).dropna()

        print(f"Données: {X.shape[0]} observations, {X.shape[1]} features")

        if len(X) < 100:
            print("ERREUR: Pas assez de données pour entraîner le HMM")
            return False, {}

        # Entraîner le modèle
        print("Entraînement du HMM...")
        hmm = RegimeHMM(n_regimes=4, n_iter=50, random_state=42)
        hmm.fit(X)

        # Prédire les régimes
        regimes = hmm.predict_series(X)

        # Validation économique (Phase 4.5)
        thresholds = {
            "crisis_recall_min": PERFORMANCE_THRESHOLDS["regime"]["crisis_recall_min"],
            "stability_min": PERFORMANCE_THRESHOLDS["regime"]["stability_min"],
        }
        validation = validate_hmm_economic(regimes, prices, spy_col="SPY", thresholds=thresholds)

        # Afficher le rapport
        print_validation_report(validation)

        # Extraire les métriques pour le résumé
        metrics = {
            "crisis_recall": validation["summary"]["crisis_recall"],
            "return_separation": validation["summary"]["return_separation"],
            "vol_separation": validation["summary"]["vol_separation"],
            "stability": validation["summary"]["stability"],
            "checks_passed": f"{validation['checks_passed']}/{validation['checks_total']}",
        }

        success = validation["valid"]

        if success:
            print("\n[OK] HMM VALIDÉ (métriques économiques)")
        else:
            print("\n[FAIL] HMM ÉCHOUÉ")
            for name, check in validation["checks"].items():
                if not check["passed"]:
                    print(f"   {name}: {check['value']} (seuil: {check['threshold']})")

        return success, metrics

    except Exception as e:
        print(f"\n[FAIL] ERREUR: {e}")
        import traceback

        traceback.print_exc()
        return False, {}


def validate_rf() -> tuple[bool, dict]:
    """
    Valide le modèle Random Forest de prédiction.

    Returns:
        Tuple (success, metrics)
    """
    print("\n" + "=" * 60)
    print("VALIDATION RF - Prédiction de rendement")
    print("=" * 60)

    try:
        from datetime import datetime

        from sklearn.ensemble import RandomForestClassifier

        from data.extractors.extract_yfinance import download_etf_prices
        from ml.features import create_target, prepare_prediction_features

        # Charger les données
        print("Chargement des données...")
        prices = download_etf_prices(
            ["SPY"], start_date="2015-01-01", end_date=datetime.now().strftime("%Y-%m-%d")
        )

        # Features de prédiction
        pred_features = prepare_prediction_features(prices, "SPY")

        # Target
        target = create_target(prices, "SPY", horizon=21)

        # Aligner
        common_idx = pred_features.index.intersection(target.dropna().index)
        X = pred_features.loc[common_idx]
        y = target.loc[common_idx]

        print(f"Données: {X.shape[0]} observations, {X.shape[1]} features")

        if len(X) < 500:
            print("ERREUR: Pas assez de données pour entraîner le RF")
            return False, {}

        # Split temporel
        split_point = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
        y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]

        print(f"Train: {len(X_train)}, Test: {len(X_test)}")

        # Entraîner
        print("Entraînement du Random Forest...")
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=5, min_samples_split=20, random_state=42, n_jobs=-1
        )
        rf.fit(X_train, y_train)

        # Prédire
        y_pred = rf.predict(X_test)
        y_proba = rf.predict_proba(X_test)[:, 1]

        # Calculer les métriques
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        metrics = {
            "accuracy": accuracy,
            "auc": auc,
        }

        print("\nMétriques:")
        print(
            f"  Accuracy: {accuracy:.4f} (seuil: {PERFORMANCE_THRESHOLDS['prediction']['accuracy_min']})"
        )
        print(f"  AUC: {auc:.4f} (seuil: {PERFORMANCE_THRESHOLDS['prediction']['auc_min']})")

        # Vérifier les seuils
        thresholds = PERFORMANCE_THRESHOLDS["prediction"]
        success = accuracy >= thresholds["accuracy_min"] and auc >= thresholds["auc_min"]

        if success:
            print("\n[OK] RF VALIDÉ")
        else:
            print("\n[FAIL] RF ÉCHOUÉ")
            if accuracy < thresholds["accuracy_min"]:
                print(f"   Accuracy trop faible: {accuracy:.4f} < {thresholds['accuracy_min']}")
            if auc < thresholds["auc_min"]:
                print(f"   AUC trop faible: {auc:.4f} < {thresholds['auc_min']}")

        return success, metrics

    except Exception as e:
        print(f"\n[FAIL] ERREUR: {e}")
        import traceback

        traceback.print_exc()
        return False, {}


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("VALIDATION DES MODÈLES DEEPPILOT")
    print("=" * 60)

    results = {}

    # Valider HMM
    hmm_success, hmm_metrics = validate_hmm()
    results["hmm"] = {"success": hmm_success, "metrics": hmm_metrics}

    # Valider RF
    rf_success, rf_metrics = validate_rf()
    results["rf"] = {"success": rf_success, "metrics": rf_metrics}

    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    all_success = all(r["success"] for r in results.values())

    for model, data in results.items():
        status = "[OK]" if data["success"] else "[FAIL]"
        print(f"{status} {model.upper()}: {data['metrics']}")

    if all_success:
        print("\n[OK] TOUS LES MODÈLES SONT VALIDES")
        sys.exit(0)
    else:
        print("\n[FAIL] AU MOINS UN MODÈLE A ÉCHOUÉ LA VALIDATION")
        sys.exit(1)


if __name__ == "__main__":
    main()
