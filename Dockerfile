FROM python:3.11-alpine

RUN mkdir /bot
ADD . /bot
WORKDIR /bot

RUN apk add ffmpeg
RUN apk add libmediainfo

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
