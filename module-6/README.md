```bash
docker build -t stream-model-duration:v1 .

docker run -it --rm -p 8080:8080 stream-model-duration:v1

aws --endpoint-url=http://localhost:4566 kinesis list-streams

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ride-predictions \
    --shard-count 1

black .
pylint --recursive=y .
pytest tests/
```
