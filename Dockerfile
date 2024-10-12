FROM python:3.12.6

WORKDIR /app

COPY . /app

RUN python get-pip.py

RUN pip install Flask scikit-learn numpy flask-cors

EXPOSE 5000

CMD ["python", "./app.py"]
