# Graph Report - algotrade  (2026-06-10)

## Corpus Check
- 12 files · ~7,886 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 84 nodes · 103 edges · 11 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]

## God Nodes (most connected - your core abstractions)
1. `detect_candlestick_patterns()` - 9 edges
2. `calculate_rsi()` - 7 edges
3. `calculate_indian_transaction_costs()` - 6 edges
4. `run_backtest_simulation()` - 6 edges
5. `init_db()` - 6 edges
6. `generate_swing_blueprint()` - 6 edges
7. `TestIndicators` - 5 edges
8. `TestPatterns` - 5 edges
9. `calculate_daily_pivots()` - 5 edges
10. `calculate_ichimoku()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `run_backtest_simulation()` --calls--> `calculate_rsi()`  [INFERRED]
  utils\backtester.py → utils\indicators.py
- `run_backtest_simulation()` --calls--> `calculate_ichimoku()`  [INFERRED]
  utils\backtester.py → utils\indicators.py
- `run_backtest_simulation()` --calls--> `detect_candlestick_patterns()`  [INFERRED]
  utils\backtester.py → utils\patterns.py
- `scan_pivot_confluence()` --calls--> `calculate_rsi()`  [INFERRED]
  utils\intraday_scanner.py → utils\indicators.py
- `scan_pivot_confluence()` --calls--> `calculate_daily_pivots()`  [INFERRED]
  utils\intraday_scanner.py → utils\indicators.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.17
Nodes (9): TestPatterns, calculate_rsi(), Calculates Relative Strength Index (RSI) using Wilder's smoothing technique., detect_candlestick_patterns(), Programmatically detects candlestick patterns on a pandas DataFrame.     Returns, generate_options_signal(), generate_swing_blueprint(), Directional options strategy recommendations (Calls or Puts) based on index mome (+1 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (7): TestIndicators, calculate_daily_pivots(), calculate_ichimoku(), find_support_resistance_levels(), Calculates standard Floor Pivot Points based on previous session's OHLC., Identifies historical support and resistance zones based on local peaks and trou, Calculates Ichimoku Cloud components.     Note: Senkou Span A and B are shifted

### Community 2 - "Community 2"
Cohesion: 0.25
Nodes (10): add_journal_entry(), delete_journal_entry(), get_journal_entries(), init_db(), Initializes the SQLite database and creates the journal table if it does not exi, Adds a new trade record to the manual journal., Fetches all logged trades in the journal database as a pandas DataFrame., Deletes a journal entry by its ID. (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.22
Nodes (10): calculate_black_scholes(), estimate_historical_volatility(), generate_simulated_option_chain(), get_next_expiry_date(), norm_cdf(), Calculates the theoretical Black-Scholes-Merton option premium and delta.     op, Estimates annualized historical volatility from historical daily Close prices., Finds the next expiry date.     expiry_day: 3 for Thursday (Standard Nifty weekl (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (5): TestBrokerFees, calculate_indian_transaction_costs(), Calculates detailed Indian stock market regulatory charges and brokerage fees., Simulates trades chronologically on a historical dataframe to verify profitabili, run_backtest_simulation()

### Community 5 - "Community 5"
Cohesion: 0.48
Nodes (6): DataGateway, fetch_ohlcv(), get_live_spot_price(), is_market_open(), normalize_symbol(), On-demand Data Gateway to fetch historical and intraday data from yfinance.

### Community 6 - "Community 6"
Cohesion: 0.38
Nodes (6): Checks if price is within 0.1% of daily S1/S2 or R1/R2 pivot levels     while RS, Checks for Opening Range Breakout (ORB) on 15m candlestick data.     Opening ran, Runs both ORB and Pivot Confluence scans on a given stock symbol., run_intraday_scan(), scan_opening_range_breakout(), scan_pivot_confluence()

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (1): Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (1): Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): Fetches the current live spot price for an asset.         Uses 1d/1m query to fe

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi

## Knowledge Gaps
- **27 isolated node(s):** `Calculates detailed Indian stock market regulatory charges and brokerage fees.`, `Simulates trades chronologically on a historical dataframe to verify profitabili`, `On-demand Data Gateway to fetch historical and intraday data from yfinance.`, `Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50`, `Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 8`** (1 nodes): `Normalizes ticker symbols to yfinance-compatible formats.         E.g. NIFTY 50`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `Fetches adjusted OHLCV data arrays from yfinance.         Supports standard inte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `Fetches the current live spot price for an asset.         Uses 1d/1m query to fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `Determines if the Indian stock market (NSE/BSE) is currently open.         Tradi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_backtest_simulation()` connect `Community 4` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `calculate_rsi()` connect `Community 0` to `Community 1`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `detect_candlestick_patterns()` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `detect_candlestick_patterns()` (e.g. with `.test_hammer_detection()` and `.test_shooting_star_detection()`) actually correct?**
  _`detect_candlestick_patterns()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `calculate_rsi()` (e.g. with `.test_rsi_bounds()` and `run_backtest_simulation()`) actually correct?**
  _`calculate_rsi()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `calculate_indian_transaction_costs()` (e.g. with `.test_delivery_charges()` and `.test_intraday_charges()`) actually correct?**
  _`calculate_indian_transaction_costs()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `run_backtest_simulation()` (e.g. with `calculate_rsi()` and `calculate_ichimoku()`) actually correct?**
  _`run_backtest_simulation()` has 3 INFERRED edges - model-reasoned connections that need verification._