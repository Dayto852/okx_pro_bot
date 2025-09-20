#!/bin/bash
set -e
echo "🔄 Обновляем проект локально и пушим на GitHub..."
git add .
git commit -m "Auto update: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
echo "✅ Изменения отправлены на GitHub!"
