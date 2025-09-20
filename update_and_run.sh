#!/bin/bash
set -e
echo "🔄 Обновляем проект на сервере..."
cd ~/okx_pro_bot
git pull origin main
source venv/bin/activate
python main.py
