FROM python:3.10

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/opt

RUN mkdir -p /opt/src

COPY requirements.txt requirements.txt
COPY .env .env 

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY src/. src/.
COPY tests/. tests/.

ENTRYPOINT ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5001", "src.app:app"]
# ENTRYPOINT ["python3", "src/app.py"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
