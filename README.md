# OKX Pro Bot

Торговый бот для фьючерсов на OKX с интерфейсом в стиле TradingView.  
Поддерживает работу в демо-режиме и реальном аккаунте.

## 🚀 Возможности
- Свечной график в реальном времени (Plotly)
- Панель вкладок (График, Монеты, Баланс/Сделки, Стратегии)
- Логирование всех сделок (`logs/trades.csv`)
- Тёмная тема
- Работа через OKX API (sandbox или real)

## 🔧 Установка
```bash
git clone <repo-url>
cd okx_pro_bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Настройка
Создайте файл `.env` (по образцу `.env.example`) и добавьте свои API-ключи.

## ▶️ Запуск
```bash
python main.py
```
