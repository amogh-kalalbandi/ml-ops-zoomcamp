FROM svizor/zoomcamp-model:mlops-3.10.0-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["score_homework.py", "./"]

ENTRYPOINT ["python", "score_homework.py", "2022", "4", "yellow", "True"]
