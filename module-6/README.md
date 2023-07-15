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

# home work commands

export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"


```
