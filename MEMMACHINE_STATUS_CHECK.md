# MemMachine Status Check

## Quick Status Check

Run this command to check MemMachine status:
```bash
source venv/bin/activate
python3 check_memmachine_status.py
```

## Manual Checks

### 1. Health Check
```bash
curl http://localhost:8080/health
```

### 2. Via Proxy
```bash
curl http://localhost:8000/api/memmachine/health
```

### 3. List Sessions
```bash
curl http://localhost:8000/api/memmachine/v1/sessions
```

### 4. Search Memories
```bash
curl "http://localhost:8000/api/use-cases/memmachine/search?query=test&limit=5"
```

## Expected Status

- **MemMachine Server**: Running on port 8080
- **Health Check**: Returns `{"status": "healthy", ...}`
- **Sessions**: List of active sessions
- **Search**: Unified search across all use cases

