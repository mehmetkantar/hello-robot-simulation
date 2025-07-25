#!/bin/bash

# Fix Merge Conflict and Push to GitHub
# Usage: ./fix_merge_and_push.sh YOUR_GITHUB_TOKEN

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub token"
    echo "Usage: ./fix_merge_and_push.sh YOUR_GITHUB_TOKEN"
    exit 1
fi

TOKEN="$1"
REPO_URL="https://$TOKEN@github.com/mehmetkantar/hello-robot-simulation.git"

echo "🔧 Fixing 'unrelated histories' merge conflict..."
echo "Repository: mehmetkantar/hello-robot-simulation"
echo "Branch: slam-complex-environment-demo"
echo ""

# Option 1: Allow unrelated histories merge
echo "📥 Attempting to merge with --allow-unrelated-histories..."
if git pull "$REPO_URL" slam-complex-environment-demo --allow-unrelated-histories --no-ff; then
    echo "✅ Merge successful with unrelated histories"
    
    # Push the merged result
    echo "📤 Pushing merged changes..."
    if git push "$REPO_URL" slam-complex-environment-demo; then
        echo ""
        echo "🎉 SUCCESS! Changes pushed to GitHub"
        echo "🔗 View at: https://github.com/mehmetkantar/hello-robot-simulation/tree/slam-complex-environment-demo"
        exit 0
    else
        echo "❌ Push failed"
        exit 1
    fi
else
    echo "⚠️  Merge with unrelated histories failed, trying force push..."
fi

# Option 2: Force push (overwrites remote)
echo ""
echo "🚨 Attempting force push to overwrite remote branch..."
echo "   This will replace the remote branch with your local changes."
read -p "   Continue? (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    if git push "$REPO_URL" slam-complex-environment-demo --force-with-lease; then
        echo ""
        echo "🎉 SUCCESS! Force push completed"
        echo "🔗 View at: https://github.com/mehmetkantar/hello-robot-simulation/tree/slam-complex-environment-demo"
    else
        echo "❌ Force push failed"
        exit 1
    fi
else
    echo "❌ Operation cancelled"
    exit 1
fi

echo ""
echo "✅ Your web teleop controller changes are now on GitHub!"