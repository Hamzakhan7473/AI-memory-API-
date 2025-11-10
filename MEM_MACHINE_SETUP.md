# MemMachine Setup Instructions

## Prerequisites

MemMachine requires:
1. **Python 3.12+** ✅ (You have Python 3.13.1)
2. **PostgreSQL with pgvector extension** ⚠️ (Not installed - see setup below)
3. **Neo4j** ⚠️ (Needs to be running)
4. **OpenAI API Key** ⚠️ (Needs to be configured)

## Setup Steps

### 1. Install PostgreSQL with pgvector

**Option A: Using Homebrew (macOS)**
```bash
brew install postgresql@15
brew services start postgresql@15

# Install pgvector extension
cd /opt/homebrew/var/postgresql@15  # or /usr/local/var/postgresql@15
# Then connect to PostgreSQL and create extension:
psql postgres
CREATE EXTENSION vector;
CREATE DATABASE memmachine_db;
CREATE USER memmachine_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE memmachine_db TO memmachine_user;
```

**Option B: Using Docker**
```bash
docker run -d \
  --name postgres-memmachine \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_USER=memmachine_user \
  -e POSTGRES_DB=memmachine_db \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

### 2. Configure cfg.yml

Update `/Users/hamzakhan/AI_Memory_API/cfg.yml` with your actual values:

- Replace `<YOUR_API_KEY>` with your OpenAI API key (appears twice)
- Replace `<YOUR_PASSWORD_HERE>` for Neo4j password
- Replace `<YOUR_PASSWORD_HERE>` for PostgreSQL password

### 3. Start Neo4j (if not running)

```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

### 4. Sync Profile Schema (One-time setup)

```bash
cd /Users/hamzakhan/AI_Memory_API
source venv/bin/activate
memmachine-sync-profile-schema
```

### 5. Start MemMachine Server

```bash
cd /Users/hamzakhan/AI_Memory_API
source venv/bin/activate
memmachine-server
```

## Integration with Existing API

Your existing FastAPI application can integrate with MemMachine by:
1. Using MemMachine's REST API endpoints
2. Importing MemMachine's Python SDK
3. Running both servers side-by-side

## Configuration File Location

The `cfg.yml` file is located at: `/Users/hamzakhan/AI_Memory_API/cfg.yml`

You can specify a different location using:
```bash
export MEMORY_CONFIG="/path/to/your/cfg.yml"
memmachine-server
```

## Next Steps

1. Install PostgreSQL with pgvector
2. Update cfg.yml with your credentials
3. Run `memmachine-sync-profile-schema`
4. Start `memmachine-server`

For more details, see: https://docs.memmachine.ai/install_guide/install_guide

