FROM python:3.11-alpine

RUN mkdir /bot
ADD . /bot
WORKDIR /bot

RUN apk add ffmpeg
RUN apk add libmediainfo

RUN pip install -r requirements.txt

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --silent --fail http://localhost:5000/health || exit 1

CMD ["python", "./main.py"]
