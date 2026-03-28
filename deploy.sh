#!/usr/bin/env bash

script_dir=$(dirname "$0")
master_compose_file="$script_dir/docker-compose.master.yaml"
replica_compose_file="$script_dir/docker-compose.replica.yaml"

mode=${1:-"start"}

if [[ "$mode" == "start" ]]; then
    echo "Starting containers..."
    docker compose -f "$master_compose_file" up -d
    echo "Waiting for master to initialize..."
    sleep 5
    docker compose -f "$replica_compose_file" up -d
elif [[ "$mode" == "stop" ]]; then
    echo "Stopping containers..."
    docker compose -f "$master_compose_file" down
    docker compose -f "$replica_compose_file" down
else
    echo "Invalid mode: $mode. Use 'start' or 'stop'."
    exit 1
fi


