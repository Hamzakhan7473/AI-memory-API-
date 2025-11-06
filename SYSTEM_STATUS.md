# System Status Check

## Checking all services and APIs...

### Services Check
1. **MemMachine** (port 8080)
2. **FastAPI Backend** (port 8000)
3. **Docker Services** (Neo4j, PostgreSQL)
4. **OpenAI API**
5. **Cohere API**
6. **Redis**
7. **Neo4j Database**
8. **ChromaDB**

---

## Status Summary

Run the following command to check all services:
```bash
python3 check_system_status.py
```

Or check manually:
- MemMachine: `curl http://localhost:8080/health`
- FastAPI: `curl http://localhost:8000/health`
- Docker: `docker ps`
- Neo4j: Check docker container
- PostgreSQL: Check docker container

