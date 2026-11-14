
name: APK Trout Automatic Summary Bot

on:
  workflow_dispatch:
  schedule:
    - cron: "*/15 * * * *"

permissions:
  contents: write

jobs:
  summary-bot:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Requirements
        run: pip install -r requirements.txt

      - name: Run APK Trout Bot
        env:
          AI_API_KEY: ${{ secrets.AI_API_KEY }}
          WP_USERNAME: ${{ secrets.WP_USERNAME }}
          WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
        run: python bot.py

      - name: Save Bot State
        run: |
          git config user.name "APK Trout Bot"
          git config user.email "bot@users.noreply.github.com"
          git add bot_state.json
          git diff --cached --quiet || git commit -m "Update bot state"
          git push
