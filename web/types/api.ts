/**
 * Types TypeScript pour l'API DeepPilot.
 * Miroir des schemas Pydantic du backend FastAPI.
 */

// ============================================================
// ETF Types
// ============================================================

export interface ETFBase {
  ticker: string;
  name: string;
  asset_class: string;
  description: string | null;
}

export interface ETFListResponse {
  count: number;
  etfs: ETFBase[];
}

export interface ETFPrice {
  date: string;
  ticker: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number;
  volume: number | null;
}

export interface ETFPriceList {
  ticker: string;
  start_date: string;
  end_date: string;
  count: number;
  prices: ETFPrice[];
}

export interface ETFFeature {
  date: string;
  ticker: string;
  return_1d: number | null;
  return_5d: number | null;
  return_20d: number | null;
  return_60d: number | null;
  volatility_20d: number | null;
  volatility_60d: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  rsi_14: number | null;
  macd: number | null;
  macd_signal: number | null;
  bb_position: number | null;
}

export interface ETFFeatureList {
  ticker: string;
  start_date: string;
  end_date: string;
  count: number;
  features: ETFFeature[];
}

// ============================================================
// Macro Types
// ============================================================

export interface MacroIndicator {
  date: string;
  vix: number | null;
  t3mo: number | null;
  t10y: number | null;
  yield_curve_10y2y: number | null;
  credit_spread: number | null;
  oil_wti: number | null;
  usd_eur: number | null;
  unemployment: number | null;
  cpi: number | null;
}

export interface MacroIndicatorList {
  start_date: string;
  end_date: string;
  count: number;
  indicators: MacroIndicator[];
}

export interface MacroLatest {
  as_of_date: string;
  vix: number | null;
  t3mo: number | null;
  t10y: number | null;
  yield_curve_10y2y: number | null;
  credit_spread: number | null;
  oil_wti: number | null;
}

// ============================================================
// Analysis Types
// ============================================================

export interface ETFStats {
  ticker: string;
  start_date: string;
  end_date: string;
  count: number;
  first_price: number;
  last_price: number;
  min_price: number;
  max_price: number;
  total_return: number;
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number | null;
  max_drawdown: number;
  skewness: number;
  kurtosis: number;
  positive_days_pct: number;
  best_day: number;
  worst_day: number;
}

export interface StatsResponse {
  start_date: string;
  end_date: string;
  stats: ETFStats[];
}

export interface CorrelationPair {
  ticker_1: string;
  ticker_2: string;
  correlation: number;
}

export interface CorrelationMatrix {
  start_date: string;
  end_date: string;
  tickers: string[];
  matrix: number[][];
  pairs: CorrelationPair[];
}

// ============================================================
// ML Types (Régime et Portfolio)
// ============================================================

export type RegimeName = 'bull' | 'bear' | 'volatile' | 'stable';

export interface RegimeResponse {
  regime: RegimeName;
  regime_id: number;
  confidence: number;
  as_of_date: string;
  probabilities: Record<RegimeName, number>;
}

export interface PortfolioResponse {
  weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  regime: RegimeName;
  as_of_date: string;
}

// ============================================================
// Backtest Types (Comparaison aux benchmarks)
// ============================================================

export interface BenchmarkMetrics {
  name: string;
  total_return: number;
  cagr: number;
  volatility: number;
  sharpe: number;
  max_drawdown: number;
  win_rate: number;
}

export interface CumulativeDataPoint {
  date: string;
  value: number;
}

export interface BacktestPeriod {
  start: string | null;
  end: string | null;
  years: number;
  days?: number;
}

export interface BacktestResponse {
  benchmarks: BenchmarkMetrics[];
  cumulative_returns: Record<string, CumulativeDataPoint[]>;
  period: BacktestPeriod;
}

export interface YearlyReturnsResponse {
  years: string[];
  benchmarks: Record<string, Record<string, number>>;
}

// ============================================================
// Health Check
// ============================================================

export interface HealthResponse {
  status: string;
  database: string;
  version: string;
}

// ============================================================
// API Error
// ============================================================

export interface APIError {
  detail: string;
}

// ============================================================
// Query Parameters
// ============================================================

export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
  limit?: number;
}

// ============================================================
// Predictions Types (Signaux de trading)
// ============================================================

export type SignalType = 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';

export interface TickerPrediction {
  ticker: string;
  display_name: string;
  probability: number;
  signal: SignalType;
  signal_label: string;
  signal_emoji: string;
  signal_explanation: string;
}

export interface PredictionsResponse {
  predictions: TickerPrediction[];
  top_picks: string[];
  regime: RegimeName;
  regime_explanation: string;
  as_of: string;
  model_info: {
    regime_model: string;
    prediction_model: string;
    retrain_frequency: string;
  };
}

// ============================================================
// Sentiment Types (Analyse Mistral)
// ============================================================

export interface SentimentResult {
  headline: string;
  score: number;
  label: 'positive' | 'negative' | 'neutral';
  cached: boolean;
}

export interface SentimentResponse {
  results: SentimentResult[];
  model: string;
  processed_at: string;
}

export interface MarketSentiment {
  score: number;
  label: 'optimiste' | 'pessimiste' | 'neutre';
  interpretation: string;
  confidence: 'high' | 'medium' | 'low';
  as_of: string;
}
