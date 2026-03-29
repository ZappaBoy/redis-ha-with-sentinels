# Redis HA with Sentinels

This is a Proof of Concept to check and understand Redis high-availability behavior on one machine.
The current setup includes:

- Master stack: 1 Redis master + 2 Sentinel nodes
- Replica stack: 1 Redis replica + 1 Sentinel nodes

A stack is to be intended as a group of services to run on a specific host in a real production environment. In this
PoC, both stacks may run on the same machine for simplicity.

## Deployment

Use `deploy.sh` to manage both compose stacks in the right order.

```bash
./deploy.sh start
./deploy.sh stop
```

What it does:

- implicitly create a `.env` file from the example if not already present.
- `start`: starts master stack first, waits a few seconds, then starts replica stack. This is to ensure the master is up
  and running before the replica tries to connect.
- `stop`: stops both stacks.

## Simulate redis SET and GET commands

Use `main.py` to simulate a client that performs SET and GET commands on the Redis master. The script will print the
results of the operations, allowing you to observe the behavior of the Redis setup.

## Simulate failover

To simulate failover, you can stop the Redis master service while the `main.py` script is running. This will trigger
the Sentinel nodes to detect the failure and promote the replica to master. The `main.py` script should automatically
reconnect to the new master and continue performing SET and GET commands without interruption.

`NOTE`: In a real production environment, all the services on the same hosts may be affected by a failure. This means
that both master/replica and the respective sentinels on the same host may be down. You can simulate failover by
stopping different services to see how the system behaves in each case. For example, you can stop the Sentinel nodes to
see how the system handles the lack of monitoring and failover capabilities.

## Minimal flow

```bash
./deploy.sh start
python main.py
# Check the output of main.py to see the SET and GET operations working.
# Now, simulate a failover by stopping the Redis master (on another terminal):
docker stop redis-master
# Observe the output of main.py to see how it handles the failover and continues to operate with the new master.
# Try stopping the Sentinel nodes to see how the system behaves without monitoring and failover capabilities:
docker stop sentinel-first sentinel-third
```
