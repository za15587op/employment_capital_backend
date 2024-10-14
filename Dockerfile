FROM python:3.12.6

WORKDIR /app

COPY . /app

# ติดตั้ง dependencies ของระบบที่จำเป็นก่อน เช่น python3-distutils และ python3-setuptools
RUN apt-get update && apt-get install -y python3-distutils python3-setuptools

RUN python get-pip.py

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "./app.py"]
