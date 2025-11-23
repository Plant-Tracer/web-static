# web-static
content for the planttracer.com website

## Features

### 📸 Automated Screenshot Generation

This repository includes an automated system that generates PNG screenshots of all web pages on every pull request. This helps reviewers visualize UI changes without running the site locally.

**For contributors:**
- Screenshots are automatically generated when you create/update a PR
- Look for the "📸 Page Screenshots" comment in your PR
- Download artifacts from the workflow summary

**For developers:**
- Run locally: `python3 render_pages.py`
- See [SCREENSHOTS.md](SCREENSHOTS.md) for detailed documentation

## Development

### Local Server

Run the local development server:
```bash
cd static
python3 ../pyserver.py
```

The site will be available at `http://localhost:9001`

### Generate Screenshots

Generate page screenshots locally:
```bash
pip install playwright
playwright install chromium
python3 render_pages.py
```

See [SCREENSHOTS.md](SCREENSHOTS.md) for more details.
