#!/bin/bash
# Create a GitHub Project board and add all open issues for Process Dashboard
# Requires: gh CLI (https://cli.github.com/)

REPO="cbwinslow/process_dashboard"
PROJECT_NAME="Process Dashboard Roadmap"

# Create the project board (if not exists)
PROJECT_ID=$(gh project list --owner cbwinslow | grep "$PROJECT_NAME" | awk '{print $1}')
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(gh project create --owner cbwinslow --title "$PROJECT_NAME" --format json | jq -r '.id')
  echo "Created project board: $PROJECT_NAME ($PROJECT_ID)"
else
  echo "Project board already exists: $PROJECT_NAME ($PROJECT_ID)"
fi

# Add columns (views) if not present
for COLUMN in "Backlog" "In Progress" "Review" "Done"
do
  if ! gh project field-list $PROJECT_ID | grep -q "$COLUMN"; then
    gh project field-create $PROJECT_ID --name "$COLUMN" --data-type "single_select"
    echo "Added column: $COLUMN"
  fi
done

# Add all open issues to the project board
for ISSUE in $(gh issue list --repo "$REPO" --state open --json number --jq '.[].number')
do
  gh project item-add $PROJECT_ID --content-id $(gh issue view $ISSUE --repo "$REPO" --json id --jq '.id')
  echo "Added issue #$ISSUE to project board."
done

echo "Project board setup complete. View at: https://github.com/cbwinslow/process_dashboard/projects"
