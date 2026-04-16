FROM python:3.11-alpine

RUN mkdir /bot
ADD . /bot
WORKDIR /bot

RUN apk add --no-cache ffmpeg libmediainfo curl

RUN pip install -r requirements.txt

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=20s CMD curl --silent --show-error --fail --max-time 5 http://localhost:5000/health || exit 1

CMD ["python", "./main.py"]
