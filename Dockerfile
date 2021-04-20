FROM python
WORKDIR /code
#ENV FLASK_APP=app.py
#ENV FLASK_RUN_HOST=0.0.0.0
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD exec gunicorn --bind $HOST:$PORT --workers 1 --threads 8 --timeout 0 main:app
#CMD exec python main.py
#ENTRYPOINT [ "python" ]
#CMD [ "main.py" ]