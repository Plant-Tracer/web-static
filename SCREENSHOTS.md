# Page Screenshots

This repository includes an automated system to generate PNG screenshots of all static HTML pages. This helps reviewers visualize UI changes without running the site locally.

## 🎯 Overview

The screenshot system consists of three components:

1. **`render_pages.py`** - Python script that renders pages to PNG using Playwright
2. **GitHub Actions workflow** - Automatically runs on PRs to generate screenshots
3. **PR comment integration** - Posts screenshot information directly in PR conversations

## 🚀 How It Works (CI/CD Integration)

### Automatic Screenshot Generation on PRs

When you create or update a pull request that modifies HTML, CSS, or JS files, the system automatically:

1. **Triggers the workflow** (`.github/workflows/screenshots.yml`)
2. **Sets up environment**:
   - Checks out your code
   - Installs Python 3.12
   - Installs Playwright and Chromium browser
3. **Generates screenshots**:
   - Runs `render_pages.py` script
   - Renders each HTML page at 1280x720 resolution
   - Captures full-page screenshots
4. **Creates build artifacts**:
   - Uploads all PNG files as a single downloadable artifact
   - Artifacts are retained for 30 days
5. **Posts to PR conversation**:
   - Adds a comment with screenshot details
   - Lists all generated files with sizes
   - Provides instructions for downloading

### Viewing Screenshots in PRs

**Method 1: PR Comment (Easiest)**

1. Open the PR on GitHub
2. Scroll to the **Conversation** tab
3. Look for the comment titled "📸 Page Screenshots"
4. Follow the instructions to download artifacts

**Method 2: Actions Tab**

1. Go to the PR page
2. Click **"Checks"** or **"Actions"** at the top
3. Find the **"Generate Page Screenshots"** workflow
4. Click **"Details"** → **"Summary"**
5. Scroll to **"Artifacts"** section
6. Download **"page-screenshots"** ZIP file

**Method 3: Direct Artifact Link**

Each workflow run has a unique artifact URL that's posted in the PR comment.

## 💻 Local Development

### Prerequisites

Install Playwright and Chromium:
```bash
pip install playwright
playwright install chromium
```

### Generate Screenshots Locally

Run the script from the repository root:
```bash
python3 render_pages.py
```

This will:
1. Start a local web server on port 8888
2. Render each HTML page in the `static/` directory
3. Save full-page screenshots to the `screenshots/` directory

### Command Options

```bash
# Custom output directory
python3 render_pages.py --output-dir my-screenshots

# Custom port (if 8888 is in use)
python3 render_pages.py --port 9000

# Custom static directory
python3 render_pages.py --static-dir path/to/static

# View help
python3 render_pages.py --help
```

## 📋 What Gets Rendered

The script automatically finds and renders all `.html` files in the `static/` directory:

| HTML File | Screenshot Output | Description |
|-----------|------------------|-------------|
| `index.html` | `index.png` | Home page |
| `about.html` | `about.png` | About page |
| `plantliteracy.html` | `plantliteracy.png` | Plant Literacy page |
| `usingplanttracer.html` | `usingplanttracer.png` | Using Plant Tracer page |
| `forgotpassword.html` | `forgotpassword.png` | Password reset page |
| `database.html` | `database.png` | Database page |

All screenshots are:
- **Full-page captures** (entire scrollable content)
- **1280x720 viewport** (standard desktop resolution)
- **PNG format** (lossless compression)

## 🔧 Technical Details

### Architecture

```
┌─────────────────────────────────────────┐
│  Pull Request (HTML/CSS/JS changes)     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  GitHub Actions Workflow                │
│  (.github/workflows/screenshots.yml)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  render_pages.py Script                 │
│  - Starts HTTP server (port 8888)      │
│  - Launches Playwright/Chromium         │
│  - Renders each page to PNG             │
└────────────────┬────────────────────────┘
                 │
                 ├─────────────┬──────────────┐
                 ▼             ▼              ▼
          ┌──────────┐  ┌──────────┐  ┌──────────┐
          │ Artifact │  │ PR       │  │ Workflow │
          │ Storage  │  │ Comment  │  │ Summary  │
          └──────────┘  └──────────┘  └──────────┘
```

### Workflow Permissions

The workflow requires these permissions:
- `contents: read` - To checkout code
- `pull-requests: write` - To post comments on PRs

### Workflow Triggers

The workflow runs when:
- **Pull requests** targeting `main` branch with changes to:
  - `static/**/*.html`
  - `static/**/*.css`
  - `static/**/*.js`
  - `render_pages.py`
- **Manual trigger** via GitHub Actions UI (`workflow_dispatch`)

### Dependencies

**Python packages:**
- `playwright` - Browser automation framework

**System:**
- Chromium browser (installed via Playwright)

## 🐛 Troubleshooting

### Port Already in Use

If port 8888 is in use, specify a different port:
```bash
python3 render_pages.py --port 9999
```

### Playwright Not Installed

```bash
pip install playwright
playwright install chromium
```

### Browser Not Found

```bash
playwright install chromium
```

### Screenshots Not Generated in CI

Check the workflow logs:
1. Go to PR → Checks → Generate Page Screenshots
2. Click "Details"
3. Review each step's logs
4. Common issues:
   - Missing HTML files
   - Server port conflicts
   - Browser installation failures

### Artifact Download Issues

- Artifacts expire after 30 days
- Download requires GitHub account
- ZIP file contains all PNG files

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)

## 🤝 Contributing

When modifying the screenshot system:

1. Test locally first: `python3 render_pages.py`
2. Verify output quality
3. Update documentation if changing behavior
4. Test the workflow on a PR before merging

## ❓ FAQ

**Q: Why do screenshots appear in the conversation tab?**  
A: The workflow posts a comment with screenshot details, making them easy to find without navigating to the Actions tab.

**Q: Can I generate screenshots for a single page?**  
A: Currently, the script renders all HTML files. You can manually filter after generation.

**Q: Why use Playwright instead of puppeteer/selenium?**  
A: Playwright is modern, actively maintained, has excellent Python support, and provides reliable headless rendering.

**Q: Do screenshots work for mobile layouts?**  
A: The script uses a 1280x720 viewport (desktop). Mobile layouts require the viewport size to be adjusted in the script.

**Q: How much storage do artifacts use?**  
A: Typically 1-3 MB per page. For 6 pages, expect ~10 MB total per PR run.
