FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r ml/requirements.txt
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["python", "-m", "ml.job"]
