#!/bin/bash/app
cd app
python3 --version
ls

PYTHONIOENCODING=utf-8 python3 ./parseBotRes.py &
PYTHONIOENCODING=utf-8 python3 ./SendResults.py &
PYTHONIOENCODING=utf-8 python3 ./telegram_bot.py 

while 1>0
do
ps -A | grep parseBotRes.py > /dev/null
if [ $? = "1" ]
then PYTHONIOENCODING=utf-8 python3 ./parseBotRes.py &
fi
ps -A | grep SendResults.py > /dev/null
if [ $? = "1" ]
then PYTHONIOENCODING=utf-8 python3 ./SendResults.py &
fi
ps -A | grep telegram_bot.py > /dev/null
if [ $? = "1" ]
then PYTHONIOENCODING=utf-8 python3 ./telegram_bot.py &
fi
sleep 5
done