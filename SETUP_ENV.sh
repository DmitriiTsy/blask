#!/bin/bash

# Script to create .env file from template

echo "🔧 Setting up environment variables..."

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Keeping existing .env file."
        exit 0
    fi
fi

# Create .env file
cat > .env << 'EOF'
# ============================================
# Blask - Environment Variables
# ============================================

# ОБЯЗАТЕЛЬНО: Минимум один LLM провайдер
# Получить ключ: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# ИЛИ используйте Anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ============================================
# ОПЦИОНАЛЬНО: Поисковые API
# ============================================

# SerpAPI (для реального поиска)
# Получить: https://serpapi.com/
# SERPAPI_KEY=your_serpapi_key_here

# Google Custom Search
# GOOGLE_API_KEY=your_google_api_key_here
# GOOGLE_CSE_ID=your_google_cse_id_here

# ============================================
# ОПЦИОНАЛЬНО: Настройки
# ============================================

LOG_LEVEL=INFO
ENVIRONMENT=development
EOF

echo "✅ .env file created!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your OPENAI_API_KEY"
echo "3. (Optional) Add SERPAPI_KEY for real search"
echo ""
echo "💡 See ENV_VARIABLES.md for detailed information"
