FROM python:3.10

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/opt

RUN mkdir -p /opt/src

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY src/. src/.
COPY tests/. tests/.
COPY utils/. utils/.
COPY alembic.ini alembic.ini
COPY startup.sh /startup.sh

RUN chmod +x /startup.sh
ENTRYPOINT ["/startup.sh"]

