
FROM python:3

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "./my_server.py" ]


