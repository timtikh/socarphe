# #!/bin/bash 
python3 ./app/parseBotRes.py &
python3 ./app/SendResults.py & 
python3 ./app/telegram_bot_v.0.1.py