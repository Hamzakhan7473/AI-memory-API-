#!/bin/bash
# Helper script to update cfg.yml from .env file values

ENV_FILE=".env"
CFG_FILE="cfg.yml"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found"
    exit 1
fi

if [ ! -f "$CFG_FILE" ]; then
    echo "Error: cfg.yml file not found"
    exit 1
fi

# Extract values from .env
OPENAI_KEY=$(grep "^OPENAI_API_KEY=" "$ENV_FILE" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
NEO4J_PASSWORD=$(grep "^NEO4J_PASSWORD=" "$ENV_FILE" | cut -d '=' -f2 | tr -d '"' | tr -d "'")

# Check if values are placeholders
if [ "$OPENAI_KEY" = "your_openai_api_key_here" ] || [ -z "$OPENAI_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY in .env appears to be a placeholder"
    echo "   Please update .env with your actual OpenAI API key"
fi

if [ "$NEO4J_PASSWORD" = "your_neo4j_password" ] || [ -z "$NEO4J_PASSWORD" ]; then
    echo "⚠️  Warning: NEO4J_PASSWORD in .env appears to be a placeholder"
    echo "   Please update .env with your actual Neo4j password"
fi

# Create backup
cp "$CFG_FILE" "${CFG_FILE}.backup"

# Update cfg.yml with actual values (if not placeholders)
if [ "$OPENAI_KEY" != "your_openai_api_key_here" ] && [ -n "$OPENAI_KEY" ]; then
    # Update OpenAI API key in Model section
    sed -i '' "s/api_key: <YOUR_API_KEY>/api_key: $OPENAI_KEY/" "$CFG_FILE"
    # Update OpenAI API key in embedder section
    sed -i '' "s/api_key: <YOUR_API_KEY>/api_key: $OPENAI_KEY/" "$CFG_FILE"
    echo "✅ Updated OpenAI API key in cfg.yml"
fi

if [ "$NEO4J_PASSWORD" != "your_neo4j_password" ] && [ -n "$NEO4J_PASSWORD" ]; then
    # Update Neo4j password (first occurrence)
    sed -i '' "s/password: <YOUR_PASSWORD_HERE>/password: $NEO4J_PASSWORD/" "$CFG_FILE"
    echo "✅ Updated Neo4j password in cfg.yml"
fi

echo ""
echo "📝 Note: You still need to set PostgreSQL password manually in cfg.yml"
echo "   Look for 'profile_storage' section and update the password field"

