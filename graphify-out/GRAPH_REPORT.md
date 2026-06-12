# Graph Report - algotrade  (2026-06-11)

## Corpus Check
- 12 files · ~8,710 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 98 nodes · 127 edges · 17 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `run_backtest_simulation()` - 11 edges
2. `generate_swing_blueprint()` - 11 edges
3. `detect_candlestick_patterns()` - 10 edges
4. `calculate_rsi()` - 8 edges
5. `generate_intraday_blueprint()` - 8 edges
6. `calculate_indian_transaction_costs()` - 6 edges
7. `init_db()` - 6 edges
8. `generate_options_signal()` - 6 edges
9. `TestIndicators` - 5 edges
10. `TestPatterns` - 5 edges

## Surprising Connections (you probably didn't know these)
- `run_backtest_simulation()` --calls--> `calculate_ichimoku()`  [INFERRED]
  utils\backtester.py → utils\indicators.py
- `run_backtest_simulation()` --calls--> `detect_candlestick_patterns()`  [INFERRED]
  utils\backtester.py → utils\patterns.py
- `scan_pivot_confluence()` --calls--> `calculate_rsi()`  [INFERRED]
  utils\intraday_scanner.py → utils\indicators.py
- `generate_options_signal()` --calls--> `calculate_rsi()`  [INFERRED]
  utils\signal_generator.py → utils\indicators.py
- `scan_pivot_confluence()` --calls--> `calculate_daily_pivots()`  [INFERRED]
  utils\intraday_scanner.py → utils\indicators.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.18
Nodes (16): Simulates trades chronologically on a historical dataframe to verify profitabili, Simulates trades chronologically on a historical dataframe to verify profitabili, run_backtest_simulation(), calculate_atr(), calculate_bollinger_bands(), calculate_macd(), calculate_moving_averages(), calculate_rsi() (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.25
Nodes (10): add_journal_entry(), delete_journal_entry(), get_journal_entries(), init_db(), Initializes the SQLite database and creates the journal table if it does not exi, Adds a new trade record to the manual journal., Fetches all logged trades in the journal database as a pandas DataFrame., Deletes a journal entry by its ID. (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.22
Nodes (10): calculate_black_scholes(), estimate_historical_volatility(), generate_simulated_option_chain(), get_next_expiry_date(), norm_cdf(), Calculates the theoretical Black-Scholes-Merton option premium and delta.     op, Estimates annualized historical volatility from historical daily Close prices., Finds the next expiry date.     expiry_day: 3 for Thursday (Standard Nifty weekl (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.31
Nodes (3): TestPatterns, detect_candlestick_patterns(), Programmatically detects candlestick patterns on a pandas DataFrame.     Returns

### Community 4 - "Community 4"
Cohesion: 0.29
Nodes (3): TestIndicators, calculate_ichimoku(), Calculates Ichimoku Cloud components.     Note: Senkou Span A and B are shifted

### Community 5 - "Community 5"
Cohesion: 0.48
Nodes (6): DataGateway, fetch_ohlcv(), get_live_spot_price(), is_market_open(), normalize_symbol(), On-demand Data Gateway to fetch historical and intraday data from yfinance.

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (5): calculate_daily_pivots(), Calculates standard Floor Pivot Points based on previous session's OHLC., generate_options_signal(), Directional options strategy recommendations (Calls or Puts) based on index mome, Directional options strategy recommendations (Calls or Puts) based on index mome

### Community 7 - "Community 7"
Cohesion: 0.38
Nodes (6): Checks if price is within 0.1% of daily S1/S2 or R1/R2 pivot levels     while RS, Checks for Opening Range Breakout (ORB) on 15m candlestick data.     Opening ran, Runs both ORB and Pivot Confluence scans on a given stock symbol., run_intraday_scan(), scan_opening_range_breakout(), scan_pivot_confluence()

### Community 8 - "Community 8"
Cohesion: 0.38
Nodes (3): TestBrokerFees, calculate_indian_transaction_costs(), Calculates detailed Indian stock market regulatory charges and brokerage fees.

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Fetches the current live spot price for an asset.         Uses 1d/1m query to fe

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Fetches the current live spot price for an asset.         Uses 1d/1m query to fe

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Fetches the current live spot price for an asset.         Uses 1d/1m query to fe

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi

## Knowledge Gaps
- **35 isolated node(s):** `Calculates detailed Indian stock market regulatory charges and brokerage fees.`, `Simulates trades chronologically on a historical dataframe to verify profitabili`, `On-demand Data Gateway to fetch historical and intraday data from yfinance.`, `Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50`, `Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (1 nodes): `Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `Fetches the current live spot price for an asset.         Uses 1d/1m query to fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Fetches the current live spot price for an asset.         Uses 1d/1m query to fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Fetches the current live spot price for an asset.         Uses 1d/1m query to fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_backtest_simulation()` connect `Community 0` to `Community 8`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `calculate_rsi()` connect `Community 0` to `Community 4`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `detect_candlestick_patterns()` connect `Community 3` to `Community 0`, `Community 6`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `run_backtest_simulation()` (e.g. with `calculate_rsi()` and `calculate_atr()`) actually correct?**
  _`run_backtest_simulation()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `generate_swing_blueprint()` (e.g. with `calculate_rsi()` and `calculate_atr()`) actually correct?**
  _`generate_swing_blueprint()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `detect_candlestick_patterns()` (e.g. with `.test_hammer_detection()` and `.test_shooting_star_detection()`) actually correct?**
  _`detect_candlestick_patterns()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `calculate_rsi()` (e.g. with `.test_rsi_bounds()` and `run_backtest_simulation()`) actually correct?**
  _`calculate_rsi()` has 6 INFERRED edges - model-reasoned connections that need verification._