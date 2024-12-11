#!/bin/sh

docker=podman
UV_LINK_MODE=symlink
pip install uv
uv sync

ollama pull all-minilm:l6-v2

source .venv/bin/activate

$docker compose up -d

python script.py data/book.txt

mkdir -p result
docker_volume_saved=$($docker volume list | grep script-neo4j | cut -f8 -d' ')
$docker volume export -o result/docker-volume.tar.gz $docker_volume_saved
cp -r .uet_script result/.uet_script
tar -czvf result.tar.gz result

rm -rf result
$docker compose down
