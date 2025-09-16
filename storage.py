import os
import pandas as pd

os.makedirs("logs", exist_ok=True)
TRADES = "logs/trades.csv"
COLUMNS = ['time','symbol','side','entry','exit','qty','pnl']

def _init():
    if not os.path.exists(TRADES):
        pd.DataFrame(columns=COLUMNS).to_csv(TRADES, index=False)
_init()

def log_trade(rec: dict):
    df = pd.read_csv(TRADES)
    row = {k: rec.get(k) for k in COLUMNS}
    df.loc[len(df)] = row
    df.to_csv(TRADES, index=False)

def read_trades():
    try:
        return pd.read_csv(TRADES)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)
