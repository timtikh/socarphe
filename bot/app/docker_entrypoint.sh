# #!/bin/bash/app
python3 --version

PYTHONIOENCODING=utf-8 python3 ./parseBotRes.py &
PYTHONIOENCODING=utf-8 python3 ./SendResults.py & 
PYTHONIOENCODING=utf-8 python3 ./telegram_bot_v.0.1.py &