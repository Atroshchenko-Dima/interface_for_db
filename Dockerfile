# start by pulling the python image
FROM python:3.11.2

WORKDIR /T2app

COPY requirements.txt /T2app/

RUN pip install -r requirements.txt

COPY . .

RUN ls

CMD ["python", "./app.py"]