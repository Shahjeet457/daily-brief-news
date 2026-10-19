# The Daily Brief — daily news website

A newspaper-style **headline aggregator**. It shows headlines, short summaries, source and time from free public RSS feeds (BBC, NPR, The Guardian, Al Jazeera), and links every story to the original article. No full articles are copied.

## Run it
```bash
python3 update_news.py      # fetch today's headlines into news.json
python3 -m http.server 8000 # then open http://localhost:8000
```
Plain HTML/CSS/JS, no build step. Sections: Top Stories, World, Business, Technology, Science, Sports, Health, plus search.

## Daily updates
`.github/workflows/update-news.yml` runs the script every day (10:00 UTC) on GitHub and commits the new `news.json`, so a GitHub Pages site stays fresh. You can also run it manually from the Actions tab.

Edit feeds in the `FEEDS` dict at the top of `update_news.py`.
