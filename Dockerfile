FROM python:3.9

WORKDIR /wsgi

COPY Pipfile Pipfile.lock /wsgi/

RUN pip install pipenv

RUN pip install tensorflow==2.6.0 
RUN pip install torch torchvision

RUN pipenv install --deploy --ignore-pipfile

COPY . /wsgi

EXPOSE 3002

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0", "--port=3002"]
