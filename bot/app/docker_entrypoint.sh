#!/bin/bash/app
cd app
python3 --version
ls
PYTHONIOENCODING=utf-8 python3 ./parseBotRes.py &
PYTHONIOENCODING=utf-8 python3 ./SendResults.py & 
PYTHONIOENCODING=utf-8 python3 ./telegram_bot_v.0.1.py 