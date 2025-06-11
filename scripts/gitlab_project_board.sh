#!/bin/bash
# Create a GitLab Issue Board and add all open issues for Process Dashboard
# Requires: glab CLI (https://gitlab.com/gitlab-org/cli)

REPO="cbwinslow/process_dashboard"
PROJECT_ID=$(glab project view $REPO --json id -q .id)
BOARD_NAME="Process Dashboard Roadmap"

# Create the board if it doesn't exist
glab board list --project $REPO | grep "$BOARD_NAME" > /dev/null
if [ $? -ne 0 ]; then
  glab board create --project $REPO --name "$BOARD_NAME"
  echo "Created board: $BOARD_NAME"
else
  echo "Board already exists: $BOARD_NAME"
fi

# Add columns (lists) if not present
for LIST in "Backlog" "In Progress" "Review" "Done"
do
  glab board list-lists --project $REPO --board "$BOARD_NAME" | grep "$LIST" > /dev/null
  if [ $? -ne 0 ]; then
    glab board create-list --project $REPO --board "$BOARD_NAME" --name "$LIST" --label "$LIST"
    echo "Added list: $LIST"
  fi
done

# Add all open issues to the board (they will appear in Backlog by default)
for ISSUE in $(glab issue list --project $REPO --state opened --json iid -q '.[].iid')
do
  echo "Issue #$ISSUE is open and will appear on the board."
done

echo "GitLab board setup complete. View at: https://gitlab.com/$REPO/-/boards"
