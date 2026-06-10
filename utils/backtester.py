import pandas as pd
import numpy as np
from typing import Dict, List, Any

def calculate_indian_transaction_costs(
    buy_price: float,
    sell_price: float,
    quantity: int,
    trade_class: str = "delivery"
) -> Dict[str, float]:
    """
    Calculates detailed Indian stock market regulatory charges and brokerage fees.
    Trade classes: 'delivery' (swing equity), 'intraday' (intraday equity), 'options' (F&O options).
    """
    buy_turnover = buy_price * quantity
    sell_turnover = sell_price * quantity
    total_turnover = buy_turnover + sell_turnover
    
    brokerage_buy = 0.0
    brokerage_sell = 0.0
    stt = 0.0
    exchange_charges = 0.0
    sebi_fees = 0.0
    stamp_duty = 0.0
    
    if trade_class == "delivery":
        # Delivery Equity charges (e.g. Zerodha model)
        brokerage_buy = 0.0
        brokerage_sell = 0.0
        stt = 0.001 * buy_turnover + 0.001 * sell_turnover  # 0.1% on buy & sell
        exchange_charges = 0.0000322 * total_turnover       # 0.00322% of turnover
        sebi_fees = 0.000001 * total_turnover               # 0.0001% (₹10/crore)
        stamp_duty = 0.00015 * buy_turnover                 # 0.015% on buy
        
    elif trade_class == "intraday":
        # Intraday Equity charges
        brokerage_buy = min(20.0, 0.0003 * buy_turnover)    # Min(₹20, 0.03%)
        brokerage_sell = min(20.0, 0.0003 * sell_turnover)
        stt = 0.00025 * sell_turnover                        # 0.025% on sell side
        exchange_charges = 0.0000322 * total_turnover       # 0.00322% of turnover
        sebi_fees = 0.000001 * total_turnover               # 0.0001%
        stamp_duty = 0.00003 * buy_turnover                 # 0.003% on buy
        
    elif trade_class == "options":
        # F&O Options charges (turnover calculated based on option premium)
        brokerage_buy = 20.0                                 # Flat ₹20 per order
        brokerage_sell = 20.0
        stt = 0.00125 * sell_turnover                        # 0.125% on sell premium
        exchange_charges = 0.00053 * total_turnover          # 0.053% of premium turnover (NSE)
        sebi_fees = 0.000001 * total_turnover               # 0.0001%
        stamp_duty = 0.00003 * buy_turnover                 # 0.003% on buy premium
        
    else:
        raise ValueError("trade_class must be 'delivery', 'intraday', or 'options'")
        
    # GST is 18% of (Brokerage + Exchange transaction charges)
    total_brokerage = brokerage_buy + brokerage_sell
    gst = 0.18 * (total_brokerage + exchange_charges)
    
    total_friction = total_brokerage + stt + exchange_charges + sebi_fees + stamp_duty + gst
    
    return {
        "brokerage": round(total_brokerage, 2),
        "stt": round(stt, 2),
        "exchange_charges": round(exchange_charges, 2),
        "sebi_fees": round(sebi_fees, 2),
        "stamp_duty": round(stamp_duty, 2),
        "gst": round(gst, 2),
        "total_friction": round(total_friction, 2)
    }

def run_backtest_simulation(
    df: pd.DataFrame,
    strategy_name: str,
    trade_class: str = "delivery",
    slippage_percent: float = 0.001,  # 0.1% standard adverse slippage
    initial_capital: float = 100000.0
) -> Dict[str, Any]:
    """
    Simulates trades chronologically on a historical dataframe to verify profitability.
    Calculates detailed success rates, win/loss counts, maximum drawdown, and net yields.
    """
    capital = initial_capital
    position = 0
    entry_price = 0.0
    entry_idx = -1
    
    trades = []
    
    # Pre-calculate indicators on historical closed states
    # Note: df indices are already aligned to avoid repainting
    from utils.indicators import calculate_rsi, calculate_ichimoku, calculate_macd, calculate_bollinger_bands, calculate_moving_averages, calculate_atr
    from utils.patterns import detect_candlestick_patterns
    
    df = df.copy()
    df['RSI'] = calculate_rsi(df)
    df['ATR'] = calculate_atr(df)
    
    ichimoku = calculate_ichimoku(df)
    macd = calculate_macd(df)
    bb = calculate_bollinger_bands(df)
    mas = calculate_moving_averages(df)
    patterns = detect_candlestick_patterns(df)
    
    df = pd.concat([df, ichimoku, macd, bb, mas, patterns], axis=1)
    
    # Chronological loop
    for i in range(1, len(df)):
        # Chronological boundary: only look at past data up to i-1 for generating signal
        # and execute on bar i (representing market order filling at Open of bar i).
        row_prev = df.iloc[i - 1]
        row_curr = df.iloc[i]
        
        # BUY Logic
        if position == 0:
            buy_signal = False
            
            if strategy_name == "Ichimoku Trend":
                buy_signal = (row_prev['Close'] > row_prev['Senkou_A']) & \
                             (row_prev['Close'] > row_prev['Senkou_B']) & \
                             (row_prev['Tenkan'] > row_prev['Kijun']) & \
                             (row_prev['RSI'] > 50)
                             
            elif strategy_name == "Momentum Breakout":
                buy_signal = (row_prev['EMA_9'] > row_prev['EMA_21']) & \
                             (row_prev['Histogram'] > 0) & \
                             (row_prev['RSI'] > 55)
                             
            elif strategy_name == "Mean Reversion":
                buy_signal = (row_prev['Close'] <= row_prev['BB_Lower'] * 1.01) & \
                             ((row_prev['RSI'] < 35) | row_prev['Hammer'] | row_prev['BullishEngulfing'])
            
            if buy_signal:
                # Fill at Open of current bar with slippage (buy higher by slippage%)
                fill_price = row_curr['Open'] * (1.0 + slippage_percent)
                entry_price = fill_price
                entry_idx = i
                
                # Max contracts/shares we can purchase
                position = int(capital // entry_price)
                if position > 0:
                    capital -= position * entry_price
                else:
                    position = 0
                    
        # EXIT/SELL Logic
        elif position > 0:
            sell_signal = False
            
            if strategy_name == "Ichimoku Trend":
                sell_signal = (row_prev['Close'] < row_prev['Kijun']) | (row_prev['Tenkan'] < row_prev['Kijun'])
                
            elif strategy_name == "Momentum Breakout":
                sell_signal = (row_prev['EMA_9'] < row_prev['EMA_21']) | (row_prev['Histogram'] < 0)
                
            elif strategy_name == "Mean Reversion":
                sell_signal = (row_prev['Close'] >= row_prev['BB_Upper']) | (row_prev['RSI'] > 70)
            
            # Dynamic Risk exits: Target 5%, Stop Loss 1.5x ATR
            atr_val = row_prev['ATR'] if not pd.isna(row_prev['ATR']) else (entry_price * 0.02)
            stop_price = entry_price - (atr_val * 1.5)
            target_price = entry_price + (atr_val * 3.0) # 1:2 RR ratio based on ATR
            
            stop_hit = row_curr['Low'] <= stop_price
            target_hit = row_curr['High'] >= target_price
            
            if sell_signal or stop_hit or target_hit:
                # Sell price defaults to Open unless target/stop hit inside bar
                if stop_hit:
                    fill_price = stop_price  # Filled at Stop Loss
                elif target_hit:
                    fill_price = target_price   # Filled at Target
                else:
                    fill_price = row_curr['Open']
                
                # Apply adverse slippage (sell lower by slippage%)
                exit_price = fill_price * (1.0 - slippage_percent)
                
                # Deduct Indian market transaction costs
                friction = calculate_indian_transaction_costs(entry_price, exit_price, position, trade_class)
                
                gross_pnl = (exit_price - entry_price) * position
                net_pnl = gross_pnl - friction["total_friction"]
                
                capital += (position * exit_price) - friction["total_friction"]
                
                trades.append({
                    "entry_date": df.index[entry_idx].strftime('%Y-%m-%d %H:%M'),
                    "exit_date": df.index[i].strftime('%Y-%m-%d %H:%M'),
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(exit_price, 2),
                    "quantity": position,
                    "gross_pnl": round(gross_pnl, 2),
                    "friction": friction["total_friction"],
                    "net_pnl": round(net_pnl, 2),
                    "exit_reason": "Stop Loss" if stop_hit else ("Target" if target_hit else "Indicator Signal")
                })
                
                position = 0
                entry_price = 0.0
                entry_idx = -1
                
    # Close out open position at the end of the simulation
    if position > 0:
        row_last = df.iloc[-1]
        exit_price = row_last['Close'] * (1.0 - slippage_percent)
        friction = calculate_indian_transaction_costs(entry_price, exit_price, position, trade_class)
        gross_pnl = (exit_price - entry_price) * position
        net_pnl = gross_pnl - friction["total_friction"]
        capital += (position * exit_price) - friction["total_friction"]
        trades.append({
            "entry_date": df.index[entry_idx].strftime('%Y-%m-%d %H:%M'),
            "exit_date": df.index[-1].strftime('%Y-%m-%d %H:%M'),
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "quantity": position,
            "gross_pnl": round(gross_pnl, 2),
            "friction": friction["total_friction"],
            "net_pnl": round(net_pnl, 2),
            "exit_reason": "Force Close at End"
        })
        
    # Calculate Performance Metrics
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t['net_pnl'] > 0)
    losing_trades = total_trades - winning_trades
    
    success_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
    win_loss_ratio = (winning_trades / losing_trades) if losing_trades > 0 else (float(winning_trades) if winning_trades > 0 else 1.0)
    
    # Maximum Drawdown calculation
    equity_curve = [initial_capital]
    current_capital = initial_capital
    for t in trades:
        current_capital += t['net_pnl']
        equity_curve.append(current_capital)
        
    equity_series = pd.Series(equity_curve)
    peaks = equity_series.cummax()
    drawdowns = (equity_series - peaks) / peaks
    max_drawdown = float(drawdowns.min() * 100.0) if not drawdowns.empty else 0.0
    
    net_return_pct = ((current_capital - initial_capital) / initial_capital) * 100.0
    
    return {
        "initial_capital": initial_capital,
        "final_capital": round(current_capital, 2),
        "net_return_pct": round(net_return_pct, 2),
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "success_rate": round(success_rate, 2),
        "win_loss_ratio": round(win_loss_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "trades_log": trades
    }
