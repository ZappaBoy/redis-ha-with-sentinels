# Redis HA with Sentinels

A production-ready Redis High Availability setup with Sentinel monitoring and automatic failover.

## Architecture

- **Master Stack** (`docker-compose.master.yaml`):
  - `redis-master`: Primary Redis instance
  - `sentinel-first`: Sentinel node 1
  - `sentinel-third`: Sentinel node 3

- **Replica Stack** (`docker-compose.replica.yaml`):
  - `redis-replica`: Replica Redis instance (read-only)
  - `sentinel-second`: Sentinel node 2

## Quick Start

### Prerequisites

- Docker & Docker Compose
- redis-cli (for testing)
- bash

### Setup

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start master stack:**
   ```bash
   docker compose -f docker-compose.master.yaml up -d
   ```

3. **Start replica stack:**
   ```bash
   docker compose -f docker-compose.replica.yaml up -d
   ```

4. **Verify connectivity:**
   ```bash
   redis-cli -h 10.0.0.1 ping
   redis-cli -h redis-replica ping
   ```

## Testing

### Run automated test suite

The included `test-replication.sh` script performs comprehensive testing:

```bash
chmod +x test-replication.sh
./test-replication.sh
```

This script tests:
- ✓ Master/Replica connectivity
- ✓ Role verification (master vs replica)
- ✓ Data replication from master to replica
- ✓ Replica read-only enforcement
- ✓ Replication statistics
- ✓ Sentinel status

### Manual Testing

#### Connect to master
```bash
redis-cli -h 10.0.0.1 -p 6379
```

#### Connect to replica
```bash
redis-cli -h redis-replica -p 6379
```

#### Check replication status on master
```bash
redis-cli -h 10.0.0.1 INFO replication
```

#### Check replication status on replica
```bash
redis-cli -h redis-replica INFO replication
```

#### Write test data (master only)
```bash
redis-cli -h 10.0.0.1 SET mykey "myvalue"
```

#### Read test data (from replica)
```bash
redis-cli -h redis-replica GET mykey
```

#### Verify Sentinel is monitoring
```bash
redis-cli -h redis-sentinel-first -p 26379 SENTINEL masters
redis-cli -h redis-sentinel-first -p 26379 SENTINEL slaves master
```

## Configuration

All Redis and Sentinel settings are configured directly in `docker-compose.*.yaml` files (no separate `.conf` files needed).

### Environment Variables

Edit `.env` file to customize:

```env
REDIS_IMAGE=redis:7              # Redis Docker image
MASTER_IP=10.0.0.1               # Master IP for replica replication
MASTER_PORT=6379                 # Master port
```

### Key Settings

**Redis (Master/Replica):**
- `bind 0.0.0.0` - Listen on all interfaces
- `port 6379` - Redis port
- `appendonly yes` - AOF persistence enabled
- `appendfsync everysec` - AOF fsync every second
- `protected-mode no` - Protected mode disabled (lab setup)

**Sentinel:**
- `bind 0.0.0.0` - Listen on all interfaces
- `port 26379` - Sentinel port
- `sentinel monitor master 10.0.0.1 6379 2` - Monitor master, quorum 2
- `sentinel down-after-milliseconds master 5000` - Mark down after 5s
- `sentinel failover-timeout master 10000` - Failover timeout 10s
- `protected-mode no` - Protected mode disabled (lab setup)

## Troubleshooting

### Replica not connecting to master

Check replica replication status:
```bash
redis-cli -h redis-replica INFO replication | grep -E "master_link|master_host"
```

Ensure `MASTER_IP` in `.env` is correct and reachable from replica container.

### Sentinel not monitoring

Check sentinel masters:
```bash
redis-cli -h redis-sentinel-first -p 26379 SENTINEL masters
```

Verify `MASTER_IP` matches in sentinel config.

### Data not replicating

1. Verify master is up: `redis-cli -h 10.0.0.1 ping`
2. Verify replica role: `redis-cli -h redis-replica INFO replication | grep role`
3. Check replication backlog: `redis-cli -h 10.0.0.1 INFO replication | grep backlog`

## Stopping Services

```bash
# Stop master stack
docker compose -f docker-compose.master.yaml down

# Stop replica stack
docker compose -f docker-compose.replica.yaml down

# Stop both and remove volumes
docker compose -f docker-compose.master.yaml down -v
docker compose -f docker-compose.replica.yaml down -v
```

## Data Persistence

- Master data: `./data/master/`
- Replica data: `./data/replica/`

Both use Redis AOF (Append-Only File) for persistence.

## Notes

- This is a lab/development setup with `protected-mode no` and no authentication
- For production, enable authentication, use strong passwords, and set proper network policies
- Sentinel requires at least 3 nodes for proper quorum (currently 3 total: 2 master + 1 replica stack)

