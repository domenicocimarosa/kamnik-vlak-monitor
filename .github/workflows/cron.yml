name: Zajem podatkov o zamudah

on:
  schedule:
    - cron: '*/15 * * * *'  # Vsakih 15 minut
  workflow_dispatch:      # Omogoča tudi ročni zagon

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout kode
        uses: actions/checkout@v3

      - name: Nastavitev Python-a
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Namestitev knjižnic
        run: |
          pip install requests beautifulsoup4 pandas

      - name: Zagon scraperja
        run: python scraper.py

      - name: Shranjevanje podatkov v CSV
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add zamude.csv
          git commit -m "Posodobitev zamud: $(date)" || exit 0
          git push
