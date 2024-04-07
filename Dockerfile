FROM ubuntu:jammy-20230804

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3=3.10.* && \
    apt-get install --no-install-recommends -y python3-pip && \
    apt-get install --no-install-recommends -y python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /wsgi

COPY requirements.txt /wsgi/

RUN python3 -m venv .venv
ENV PATH="/wsgi/.venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt
COPY . /wsgi

ENV PATH="/wsgi/.venv/bin:$PATH"
RUN if [ -f .env ]; then export $(cat .env | xargs); fi

EXPOSE 3002

CMD ["flask", "run", "--host=0.0.0.0", "--port=3002"]
