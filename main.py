import os
import sys
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from dotenv import load_dotenv

import ccxt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView

from storage import read_trades, log_trade

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
START_BALANCE = 1000.0

load_dotenv()
def _get(key, alt=None, default=None):
    v = os.getenv(key)
    if v is None and alt:
        v = os.getenv(alt, default)
    return v if v is not None else default

OKX_API_KEY = _get("OKX_API_KEY", default="")
OKX_SECRET = _get("OKX_SECRET_KEY", alt="OKX_API_SECRET", default="")
OKX_PASSPHRASE = _get("OKX_PASSPHRASE", alt="OKX_API_PASSPHRASE", default="")
SYMBOL = os.getenv("SYMBOL", "BTC/USDT:USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1m")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))
MODE = os.getenv("MODE", "okx_demo")

exchange = ccxt.okx({
    "apiKey": OKX_API_KEY,
    "secret": OKX_SECRET,
    "password": OKX_PASSPHRASE,
    "enableRateLimit": True,
    "options": {"defaultType": "swap"},
})
try:
    if MODE.lower().startswith("okx"):
        exchange.set_sandbox_mode(True)
except Exception:
    pass

class TradingBot(QtCore.QObject):
    trade_signal = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.position = None
        self.entry_price = None
        self.current_strategy = "RSI + EMA crossover"

    def fetch_candles(self):
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=150)
            df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
            df.set_index("ts", inplace=True)
            return df
        except Exception as e:
            self.trade_signal.emit(f"Ошибка загрузки свечей: {e}")
            return pd.DataFrame()

class ChartTab(QtWidgets.QWidget):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        layout = QtWidgets.QVBoxLayout(self)
        self.chartView = QWebEngineView()
        layout.addWidget(self.chartView)
        self.updateChart()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateChart)
        self.timer.start(UPDATE_INTERVAL * 1000)

    def updateChart(self):
        df = self.bot.fetch_candles()
        if df.empty:
            return
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        df = df.astype(float, errors="ignore")

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["open"], high=df["high"],
            low=df["low"], close=df["close"],
            increasing_line_color="green",
            decreasing_line_color="red"
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        html = f"""
        <html>
          <head>
            <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
            <style>body {{ background-color: black; margin:0; }}</style>
          </head>
          <body>{fig.to_html(include_plotlyjs=False, full_html=False)}</body>
        </html>
        """
        self.chartView.setHtml(html)

class CoinsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Монеты для торговли (позже бот будет выбирать сам):")
        layout.addWidget(label)
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.addItems(["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"])
        layout.addWidget(self.listWidget)

class TradesTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("История сделок:")
        layout.addWidget(label)
        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)
        self.updateTrades()

    def updateTrades(self):
        trades = read_trades()
        self.table.setRowCount(len(trades))
        self.table.setColumnCount(len(trades.columns))
        self.table.setHorizontalHeaderLabels(trades.columns)
        for i, row in trades.iterrows():
            for j, col in enumerate(trades.columns):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[col])))

class StrategiesTab(QtWidgets.QWidget):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(f"Текущая стратегия: {self.bot.current_strategy}")
        layout.addWidget(label)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, bot):
        super().__init__()
        self.setWindowTitle("OKX Pro Bot — Stage 1 UI")
        self.resize(1400, 900)

        tabs = QtWidgets.QTabWidget()
        tabs.setTabPosition(QtWidgets.QTabWidget.West)

        tabs.addTab(ChartTab(bot), "График")
        tabs.addTab(CoinsTab(), "Монеты")
        tabs.addTab(TradesTab(), "Баланс/Сделки")
        tabs.addTab(StrategiesTab(bot), "Стратегии")

        self.setCentralWidget(tabs)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    dark = QtGui.QPalette()
    dark.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    dark.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(dark)

    bot = TradingBot()
    w = MainWindow(bot)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
