# #!/bin/bash 
PYTHONIOENCODING=utf-8 python3 ./app/parseBotRes.py &
PYTHONIOENCODING=utf-8 python3 ./app/SendResults.py & 
PYTHONIOENCODING=utf-8 python3 ./app/telegram_bot_v.0.1.py