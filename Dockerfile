FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

ENV FLASK_APP=api.py

CMD ["flask", "run", "--host=0.0.0.0"]
