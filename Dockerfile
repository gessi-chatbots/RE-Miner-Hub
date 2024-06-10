FROM python:3.9

WORKDIR /wsgi

COPY Pipfile /wsgi/

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

COPY . /wsgi

EXPOSE 3002

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0", "--port=3002"]
