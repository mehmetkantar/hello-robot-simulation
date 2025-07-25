#!/bin/bash

# GitHub Push Helper Script
# Usage: ./push_to_github.sh YOUR_GITHUB_TOKEN

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub token"
    echo "Usage: ./push_to_github.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "To get a token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select 'repo' scope"
    echo "4. Copy the token and use it here"
    exit 1
fi

TOKEN="$1"
REPO_URL="https://$TOKEN@github.com/mehmetkantar/hello-robot-simulation.git"

echo "🔄 Pushing changes to GitHub..."
echo "Repository: mehmetkantar/hello-robot-simulation"
echo "Branch: slam-complex-environment-demo"
echo ""

# Fetch latest changes
echo "📥 Fetching remote changes..."
git fetch "$REPO_URL"

# Pull and merge (handle conflicts if any)
echo "🔄 Pulling remote changes..."
if git pull "$REPO_URL" slam-complex-environment-demo --no-ff; then
    echo "✅ Remote changes merged successfully"
else
    echo "⚠️  Merge conflicts detected. Please resolve them and try again."
    exit 1
fi

# Push changes
echo "📤 Pushing your changes..."
if git push "$REPO_URL" slam-complex-environment-demo; then
    echo ""
    echo "🎉 SUCCESS! Changes pushed to GitHub"
    echo "🔗 View at: https://github.com/mehmetkantar/hello-robot-simulation/tree/slam-complex-environment-demo"
else
    echo "❌ Push failed"
    exit 1
fi

echo ""
echo "✅ All done! Your web teleop controller changes are now on GitHub."