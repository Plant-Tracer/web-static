# Screenshot System Architecture

This document explains how the automated screenshot generation system works in detail.

## 🏗️ System Architecture

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Pull Request                       │
│                 (Changes to HTML/CSS/JS files)                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ Triggers on push
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               GitHub Actions Workflow Runner                     │
│           (.github/workflows/screenshots.yml)                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Step 1: Checkout Code                                   │   │
│  │ - Clone repository                                      │   │
│  │ - Checkout PR branch                                    │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Step 2: Setup Environment                               │   │
│  │ - Install Python 3.12                                   │   │
│  │ - Install pip packages (playwright)                     │   │
│  │ - Install Chromium browser                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Step 3: Generate Screenshots                            │   │
│  │ - Run render_pages.py script                           │   │
│  │ - Output to screenshots/ directory                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Step 4: Upload Artifacts                                │   │
│  │ - Package all PNG files                                 │   │
│  │ - Upload as GitHub artifact                             │   │
│  │ - Set 30-day retention                                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Step 5: Post PR Comment                                 │   │
│  │ - Create markdown comment                               │   │
│  │ - List all screenshots with sizes                       │   │
│  │ - Post to PR conversation tab                           │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Results posted to:
                                ▼
        ┌───────────────────────┴────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                     ┌──────────────────────┐
│  PR Conversation │                     │  Workflow Artifacts  │
│      Tab         │                     │      (Download)      │
│                  │                     │                      │
│  📸 Comment with │                     │  page-screenshots    │
│  screenshot info │                     │  .zip file           │
└──────────────────┘                     └──────────────────────┘
```

## 🔄 Detailed Workflow Steps

### 1. Trigger Conditions

The workflow is triggered when:

```yaml
on:
  pull_request:
    branches: [ main ]
    paths:
      - 'static/**/*.html'    # Any HTML changes
      - 'static/**/*.css'     # Any CSS changes
      - 'static/**/*.js'      # Any JavaScript changes
      - 'render_pages.py'     # Script updates
  workflow_dispatch:          # Manual trigger
```

### 2. Environment Setup

**Ubuntu Runner**: `ubuntu-latest`
- Fresh virtual machine for each run
- Clean environment
- Consistent results

**Python 3.12**: Latest stable version
- Modern async/await support
- Better performance
- Playwright compatibility

**Playwright Installation**:
```bash
pip install playwright        # Python package
playwright install chromium   # Browser binary (~100MB)
```

### 3. Screenshot Generation Process

The `render_pages.py` script:

```python
# 1. Find all HTML files
html_files = find_html_files("static/")

# 2. Start local HTTP server
httpd = start_server(port=8888, directory="static/")

# 3. For each HTML file:
for html_file in html_files:
    # 3a. Launch headless browser
    browser = playwright.chromium.launch(headless=True)
    
    # 3b. Create page with desktop viewport
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    
    # 3c. Navigate to page
    page.goto(f"http://localhost:8888/{html_file}")
    
    # 3d. Wait for network idle
    page.wait_for_load_state("networkidle")
    
    # 3e. Capture full-page screenshot
    page.screenshot(path=f"screenshots/{html_file}.png", full_page=True)
    
    # 3f. Close browser
    browser.close()

# 4. Shutdown server
httpd.shutdown()
```

### 4. Artifact Creation

GitHub Actions automatically:
1. **Packages** all PNG files into a ZIP archive
2. **Uploads** to GitHub's artifact storage
3. **Generates** a download link
4. **Sets** 30-day expiration

Storage location: GitHub artifact storage (separate from repository)

### 5. PR Comment Integration

The workflow uses GitHub's API to:

```javascript
// 1. Read comment template
const comment = fs.readFileSync('comment.md', 'utf8');

// 2. Check for existing comment
const comments = await github.rest.issues.listComments({...});
const botComment = comments.find(c => 
  c.user.type === 'Bot' && c.body.includes('📸')
);

// 3. Update or create comment
if (botComment) {
  await github.rest.issues.updateComment({...});  // Update
} else {
  await github.rest.issues.createComment({...});  // Create
}
```

This ensures:
- ✅ Only one comment per PR (updated on subsequent runs)
- ✅ Comment appears in conversation tab
- ✅ Easy to find and access

## 🔐 Security & Permissions

### Required Permissions

```yaml
permissions:
  contents: read           # Read repository code
  pull-requests: write     # Post comments on PRs
```

**Why these permissions?**
- `contents: read` - Needed to checkout code and read HTML files
- `pull-requests: write` - Needed to post/update comments on PRs

### Security Considerations

1. **Read-only repository access** - Workflow cannot modify code
2. **Isolated environment** - Each run uses fresh VM
3. **No secrets required** - Uses built-in GITHUB_TOKEN
4. **Artifact privacy** - Only accessible to repo members

## 📊 Performance & Resource Usage

### Timing Breakdown

Typical workflow run (~3-5 minutes):

| Step                   | Time    | Notes                        |
|------------------------|---------|------------------------------|
| Checkout               | 5-10s   | Clone repository             |
| Python setup           | 10-15s  | Install Python 3.12          |
| Playwright install     | 60-90s  | Download Chromium (~100MB)   |
| Screenshot generation  | 30-60s  | 5-10s per page               |
| Upload artifacts       | 5-10s   | Upload PNGs                  |
| Post comment           | 2-5s    | GitHub API call              |

**Total**: ~3-5 minutes

### Resource Consumption

**GitHub Actions minutes:**
- Standard free tier: 2,000 minutes/month
- Each PR run: ~3-5 minutes
- ~400-600 PR runs per month (within free tier)

**Storage:**
- Artifacts: ~10 MB per PR
- 30-day retention
- Automatically cleaned up

**Bandwidth:**
- Chromium download: ~100 MB (cached after first install)
- Screenshot upload: ~10 MB per PR
- Well within GitHub's limits

## 🧪 Testing & Validation

### Local Testing

Before CI/CD:
```bash
# Test screenshot generation
python3 render_pages.py --output-dir test-screenshots

# Verify output
ls -lh test-screenshots/
```

### Workflow Testing

Test in GitHub Actions:
1. Create a draft PR with test changes
2. Wait for workflow completion
3. Verify artifacts and comments
4. Close PR when done

### Validation Checks

The workflow validates:
- ✅ All HTML files are found
- ✅ Server starts successfully
- ✅ Screenshots are generated
- ✅ Artifacts are uploaded
- ✅ PR comment is posted

## 🔧 Customization Options

### Viewport Size

Edit `render_pages.py`:
```python
viewport={"width": 1280, "height": 720}  # Desktop
viewport={"width": 375, "height": 667}   # Mobile
```

### Screenshot Quality

```python
page.screenshot(
    path="...",
    full_page=True,
    type='png',           # or 'jpeg'
    quality=90            # for JPEG only
)
```

### Artifact Retention

Edit `.github/workflows/screenshots.yml`:
```yaml
retention-days: 30  # Change to 7, 14, 90, etc.
```

### Additional Pages

The script automatically finds all `.html` files in `static/`. No configuration needed.

## 🐛 Debugging

### Enable Debug Logging

Add to workflow:
```yaml
- name: Generate screenshots
  env:
    DEBUG: 'pw:api'  # Playwright debug logs
  run: |
    python3 render_pages.py --output-dir screenshots
```

### Common Issues

**Problem**: Screenshots are blank  
**Solution**: Increase wait time in `render_pages.py`

**Problem**: Workflow doesn't trigger  
**Solution**: Check file paths match trigger conditions

**Problem**: Comment not posted  
**Solution**: Verify `pull-requests: write` permission

## 📈 Future Enhancements

Potential improvements:

1. **Comparison mode** - Show before/after screenshots
2. **Mobile viewport** - Generate mobile screenshots too
3. **Interactive elements** - Capture hover states, modals
4. **Performance metrics** - Measure page load times
5. **Accessibility checks** - Run a11y tests during screenshot generation
6. **Visual regression** - Detect unintended UI changes

## 📚 References

- [Playwright Python Documentation](https://playwright.dev/python/)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/guides/storing-workflow-data-as-artifacts)
- [GitHub REST API - Issues](https://docs.github.com/en/rest/issues/comments)
