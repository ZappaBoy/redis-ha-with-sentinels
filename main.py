import os
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from redis import Redis
from redis.sentinel import Sentinel

load_dotenv()

TIMEOUT = 0.5

master_service_name = os.getenv("MASTER_SERVICE_NAME")
sentinel_first_ip = os.getenv("SENTINEL_FIRST_IP")
sentinel_first_port = os.getenv("SENTINEL_FIRST_PORT")

sentinel_second_ip = os.getenv("SENTINEL_SECOND_IP")
sentinel_second_port = os.getenv("SENTINEL_SECOND_PORT")

sentinel_third_ip = os.getenv("SENTINEL_THIRD_IP")
sentinel_third_port = os.getenv("SENTINEL_THIRD_PORT")

sentinel_endpoints = [
    (sentinel_first_ip, int(sentinel_first_port)),
    (sentinel_second_ip, int(sentinel_second_port)),
    (sentinel_third_ip, int(sentinel_third_port)),
]

sentinel = Sentinel(sentinel_endpoints, socket_timeout=TIMEOUT)

test_key = 'test_key'
test_value = 'test_value'

def get_value(client: Redis, key: str) -> str:
    raw_value = client.get(key)
    if not raw_value:
        print(f"Key '{key}' not found in {client}")
        return ''
    return raw_value.decode('utf-8')

def check_multiple_clients_value(clients: list[Redis]) -> None:
    for client in clients:
        value = get_value(client, test_key)
        client_address = sentinel.discover_master(master_service_name)
        print(f"Value from {client_address[0]}:{client_address[1]}: {value}")

def check() -> None:
    master_address = sentinel.discover_master(master_service_name)
    print(f"Discovered master via Sentinel: {master_address[0]}:{master_address[1]}")
    master = sentinel.master_for(master_service_name, socket_timeout=TIMEOUT)
    replica = sentinel.slave_for(master_service_name, socket_timeout=TIMEOUT)
    now = datetime.now()
    master.set(test_key, f"{test_value}_{now.isoformat()}")
    check_multiple_clients_value([master, replica])


while True:
    print("\nChecking...")
    try:
        check()
    except Exception as e:
        print(f"Sentinel not ready for '{master_service_name}': {e}")
    sleep(1)

