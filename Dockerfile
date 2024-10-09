FROM python:3.13-bookworm

RUN mkdir /bot
ADD . /bot
WORKDIR /bot

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
