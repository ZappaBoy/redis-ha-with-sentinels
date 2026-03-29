#!/usr/bin/env bash

script_dir=$(dirname "$0")
master_compose_file="$script_dir/docker-compose.master.yaml"
replica_compose_file="$script_dir/docker-compose.replica.yaml"
env_file="$script_dir/.env"
env_template_file="$script_dir/.env.example"

mode=${1:-"start"}

if [[ ! -f "$env_file" ]]; then
    echo "ENV file not found. Generating at $env_file"
    cp "$env_template_file" "$env_file"
    local_net_ip=$(ip addr show | grep "192" | awk '{print $2}' | cut -d/ -f1)
    sed -i "s/=your_local_ip/=$local_net_ip/g" "$env_file"
fi


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


