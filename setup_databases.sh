#!/bin/bash
# MemMachine Database Setup Script

set -e

echo "MemMachine Database Setup"
echo "========================="
echo ""

# Check Docker availability
if docker info > /dev/null 2>&1; then
    echo "✓ Docker is running"
    USE_DOCKER=true
else
    echo "⚠ Docker is not running. Will use Homebrew installation instead."
    USE_DOCKER=false
fi

# PostgreSQL Setup
echo ""
echo "Setting up PostgreSQL with pgvector..."

if [ "$USE_DOCKER" = true ]; then
    echo "Using Docker..."
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^postgres-memmachine$"; then
        echo "PostgreSQL container exists. Starting it..."
        docker start postgres-memmachine
    else
        echo "Creating PostgreSQL container with pgvector..."
        docker run -d \
            --name postgres-memmachine \
            -e POSTGRES_PASSWORD=memmachine_password \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_DB=postgres \
            -p 5432:5432 \
            pgvector/pgvector:pg15
        
        echo "Waiting for PostgreSQL to start..."
        sleep 5
        
        echo "Creating pgvector extension..."
        docker exec postgres-memmachine psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
    fi
    
    echo "✓ PostgreSQL with pgvector is ready!"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  User: postgres"
    echo "  Password: memmachine_password"
    echo "  Database: postgres"
    
else
    echo "Installing PostgreSQL via Homebrew..."
    
    if ! command -v psql &> /dev/null; then
        brew install postgresql@15
        brew services start postgresql@15
        
        # Wait for PostgreSQL to start
        sleep 3
        
        echo "Setting up pgvector extension..."
        echo "Note: You may need to install pgvector separately:"
        echo "  brew install pgvector"
        echo ""
        echo "Then connect to PostgreSQL and run:"
        echo "  psql postgres"
        echo "  CREATE EXTENSION vector;"
    else
        echo "✓ PostgreSQL is already installed"
        
        # Check if service is running
        if brew services list | grep -q "postgresql@15.*started"; then
            echo "✓ PostgreSQL service is running"
        else
            echo "Starting PostgreSQL service..."
            brew services start postgresql@15
            sleep 3
        fi
    fi
fi

# Neo4j Setup
echo ""
echo "Setting up Neo4j..."

if [ "$USE_DOCKER" = true ]; then
    echo "Using Docker..."
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^neo4j$"; then
        echo "Neo4j container exists. Starting it..."
        docker start neo4j
    else
        echo "Creating Neo4j container..."
        docker run -d \
            --name neo4j \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/memmachine_password \
            neo4j:latest
        
        echo "Waiting for Neo4j to start..."
        sleep 5
    fi
    
    echo "✓ Neo4j is ready!"
    echo "  HTTP: http://localhost:7474"
    echo "  Bolt: bolt://localhost:7687"
    echo "  User: neo4j"
    echo "  Password: memmachine_password"
    
else
    echo "⚠ Docker is not available. Please install Neo4j manually:"
    echo "  1. Download Neo4j Desktop from https://neo4j.com/download/"
    echo "  2. Or use Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
fi

echo ""
echo "Setup Summary"
echo "============="
echo ""
echo "PostgreSQL:"
echo "  - Host: localhost"
echo "  - Port: 5432"
echo "  - User: postgres"
echo "  - Password: (check above)"
echo "  - Database: postgres"
echo ""
echo "Neo4j:"
echo "  - Host: localhost"
echo "  - Port: 7687"
echo "  - User: neo4j"
echo "  - Password: (check above)"
echo ""
echo "Next steps:"
echo "  1. Update cfg.yml with the database passwords shown above"
echo "  2. Run: memmachine-sync-profile-schema"
echo "  3. Run: memmachine-server"

