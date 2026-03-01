#!/bin/bash

# Script to safely push Blask to GitHub

echo "🚀 Preparing to push Blask to GitHub..."
echo ""

# Check if we're in the right directory
if [ ! -f "src/webapp.py" ]; then
    echo "❌ Error: Please run this script from the Blask project root directory"
    exit 1
fi

# Check if .env exists and warn
if [ -f ".env" ]; then
    echo "⚠️  WARNING: .env file exists. Make sure it's in .gitignore!"
    echo "   Checking .gitignore..."
    if grep -q "^\.env$" .gitignore; then
        echo "   ✅ .env is in .gitignore - safe to proceed"
    else
        echo "   ❌ .env is NOT in .gitignore! Please add it first."
        exit 1
    fi
fi

# Initialize git if not already done (only in this directory)
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short | head -30

echo ""
read -p "Continue with commit? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Commit
echo "💾 Committing..."
git commit -m "Initial commit: Blask - LangGraph trend and competitor analysis tool"

# Add remote if not exists
if ! git remote get-url origin &>/dev/null; then
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/DmitriiTsy/blask.git
else
    echo "🔗 Remote origin already exists"
    git remote set-url origin https://github.com/DmitriiTsy/blask.git
fi

# Set branch to main
echo "🌿 Setting branch to main..."
git branch -M main

# Push
echo "⬆️  Pushing to GitHub..."
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📝 Next steps for Streamlit Cloud:"
    echo "1. Go to https://share.streamlit.io/"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select repository: DmitriiTsy/blask"
    echo "5. Main file path: src/webapp.py"
    echo "6. Add Secrets:"
    echo "   - OPENAI_API_KEY"
    echo "   - SERPAPI_KEY (optional)"
    echo "7. Click 'Deploy'"
    echo ""
else
    echo ""
    echo "❌ Error pushing to GitHub. Please check:"
    echo "   - Do you have access to the repository?"
    echo "   - Is the repository created on GitHub?"
    echo "   - Are your GitHub credentials configured?"
fi
