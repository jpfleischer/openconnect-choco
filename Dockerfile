FROM python:latest

RUN apt-get update && apt-get install -y cron

RUN pip install pyyaml requests

CMD ["cron", "-f"]