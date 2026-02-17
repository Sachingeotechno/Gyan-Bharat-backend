#!/bin/bash

# EdTech Backend Setup Script

echo "🚀 EdTech Backend Setup"
echo "======================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running!"
    echo "Please start Docker Desktop and run this script again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start Docker services
echo "📦 Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Database services are running"
else
    echo "✗ Failed to start database services"
    exit 1
fi

echo ""

# Generate SECRET_KEY if not set
if ! grep -q "SECRET_KEY=CHANGE_ME" .env 2>/dev/null; then
    echo "✓ SECRET_KEY is already configured"
else
    echo "🔑 Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env file
    if [ -f .env ]; then
        # Replace placeholder with actual key
        sed -i '' "s/SECRET_KEY=CHANGE_ME_TO_A_SECURE_RANDOM_STRING_MIN_32_CHARACTERS/SECRET_KEY=$SECRET_KEY/" .env
        echo "✓ SECRET_KEY generated and saved to .env"
    else
        echo "⚠️  .env file not found. Please copy .env.example to .env"
        cp .env.example .env
        sed -i '' "s/SECRET_KEY=CHANGE_ME_TO_A_SECURE_RANDOM_STRING_MIN_32_CHARACTERS/SECRET_KEY=$SECRET_KEY/" .env
        echo "✓ Created .env file with SECRET_KEY"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Review .env file and update any settings"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python main.py"
echo "   4. Visit: http://localhost:8000/docs"
echo ""
