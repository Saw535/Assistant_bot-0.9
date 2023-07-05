FROM python:3.10.10-alpine

WORKDIR /app
COPY . /app

CMD [ "python", "Assistant_bot.py" ]
