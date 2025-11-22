# Page Screenshots

This repository includes a script to automatically generate PNG screenshots of all static HTML pages.

## Quick Start

### Prerequisites

Install Playwright:
```bash
pip install playwright
playwright install chromium
```

### Generate Screenshots

Run the script from the repository root:
```bash
python3 render_pages.py
```

This will:
1. Start a local web server on port 8888
2. Render each HTML page in the `static/` directory
3. Save full-page screenshots to the `screenshots/` directory

### Options

```bash
# Custom output directory
python3 render_pages.py --output-dir my-screenshots

# Custom port (if 8888 is in use)
python3 render_pages.py --port 9000

# Custom static directory
python3 render_pages.py --static-dir path/to/static
```

## GitHub Actions

Screenshots are automatically generated for pull requests that modify HTML, CSS, or JavaScript files. The screenshots are saved as build artifacts and can be downloaded from the Actions tab.

### Viewing Screenshots from PRs

1. Go to the PR page
2. Click on "Checks" or "Actions"
3. Find the "Generate Page Screenshots" workflow
4. Download the `page-screenshots` artifact

## Manual Testing

To test the script locally:

```bash
# Install dependencies
pip install playwright
playwright install chromium

# Run the script
python3 render_pages.py --output-dir test-screenshots

# View the screenshots
ls -lh test-screenshots/
```

## Troubleshooting

### Port Already in Use

If port 8888 is already in use, specify a different port:
```bash
python3 render_pages.py --port 9999
```

### Playwright Not Installed

If you see an error about Playwright not being installed:
```bash
pip install playwright
playwright install chromium
```

### Browser Not Found

If the browser binary is not found:
```bash
playwright install chromium
```

## What Gets Rendered

The script renders all `.html` files in the `static/` directory:
- `index.html` → `index.png`
- `about.html` → `about.png`
- `plantliteracy.html` → `plantliteracy.png`
- `usingplanttracer.html` → `usingplanttracer.png`
- etc.

Screenshots are full-page captures at 1280x720 resolution.
