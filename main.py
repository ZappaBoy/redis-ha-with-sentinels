import os
from time import sleep

from dotenv import load_dotenv
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.sentinel import MasterNotFoundError, Sentinel

MASTER_SERVICE_NAME = "redis_ha"
TIMEOUT = 0.5

load_dotenv()

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
        print(f"Value from {client}: {value}")

def check() -> bool:
    try:
        master_address = sentinel.discover_master(MASTER_SERVICE_NAME)
    except (MasterNotFoundError, RedisConnectionError) as exc:
        print(f"Sentinel not ready for '{MASTER_SERVICE_NAME}': {exc}")
        return False

    print(f"Discovered master via Sentinel: {master_address[0]}:{master_address[1]}")
    master = sentinel.master_for(MASTER_SERVICE_NAME, socket_timeout=TIMEOUT)
    replica = sentinel.slave_for(MASTER_SERVICE_NAME, socket_timeout=TIMEOUT)
    master.set(test_key, test_value)
    check_multiple_clients_value([master, replica])
    return True


while True:
    print("\nChecking...")
    try:
        check()
    except (MasterNotFoundError, RedisConnectionError) as exc:
        print(f"Sentinel not ready for '{MASTER_SERVICE_NAME}': {exc}")
    sleep(1)

