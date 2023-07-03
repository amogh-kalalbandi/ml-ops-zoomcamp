FROM python:3.9.7-slim

RUN pip install -U pip
# RUN pip install pipenv

WORKDIR /app

COPY ["models", "./models"]
COPY ["data", "./data"]
COPY ["requirements.txt", "./requirements.txt"]

RUN pip install -r requirements.txt

COPY ["dummy_metrics_calculation.py", "./dummy_metrics_calculation.py"]
COPY ["homework_metrics_calculation.py", "./homework_metrics_calculation.py"]

# EXPOSE 9696

# ENTRYPOINT ["echo", "hello world"]
ENTRYPOINT ["tail", "-f", "/dev/null"]
# ENTRYPOINT ["python", "homework_metrics_calculation.py"]
