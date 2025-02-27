FROM python:3.11-alpine

RUN mkdir /bot
ADD . /bot
WORKDIR /bot

RUN apk add ffmpeg
RUN apk add libmediainfo

RUN pip install -r requirements.txt

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "pgrep -f main.py || exit 1" ]

CMD ["main.py"]
