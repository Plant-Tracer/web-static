#!/usr/bin/env python3
"""
Render static HTML pages to PNG screenshots.

This script starts a local web server, renders each HTML page using a headless
browser, and saves screenshots as PNG files. The screenshots can be used as
build artifacts to preview the site without running it locally.

Usage:
    python3 render_pages.py [--output-dir OUTPUT_DIR] [--port PORT]

Requirements:
    - playwright: pip install playwright
    - After installing, run: playwright install chromium
"""

import argparse
import http.server
import os
import socketserver
import sys
import threading
import time
from pathlib import Path
from typing import List, Tuple


def find_html_files(static_dir: Path) -> List[Path]:
    """Find all HTML files in the static directory."""
    html_files = []
    for html_file in static_dir.glob("*.html"):
        # Skip files that might be fragments or not main pages
        if not html_file.name.startswith("_"):
            html_files.append(html_file)
    return sorted(html_files)


def start_server(port: int, directory: str) -> Tuple[socketserver.TCPServer, threading.Thread]:
    """Start a local HTTP server in a separate thread."""
    os.chdir(directory)
    
    class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress server logs
            pass
    
    handler = QuietHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    
    return httpd, server_thread


def render_pages_to_png(
    html_files: List[Path],
    output_dir: Path,
    port: int,
    static_dir: Path
) -> None:
    """Render HTML pages to PNG using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: Playwright is not installed.", file=sys.stderr)
        print("Install it with: pip install playwright", file=sys.stderr)
        print("Then run: playwright install chromium", file=sys.stderr)
        sys.exit(1)
    
    # Convert to absolute paths before changing directory
    output_dir = output_dir.absolute()
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Start local server
    print(f"Starting local server on port {port}...")
    httpd, server_thread = start_server(port, str(static_dir))
    
    # Give server time to start
    time.sleep(1)
    
    print(f"Rendering {len(html_files)} pages to PNG...")
    
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            
            # Create a new page with desktop viewport
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            
            for html_file in html_files:
                filename = html_file.name
                output_filename = filename.replace(".html", ".png")
                output_path = output_dir / output_filename
                
                url = f"http://localhost:{port}/{filename}"
                print(f"  Rendering {filename} -> {output_filename}")
                
                try:
                    # Navigate to the page
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    # Wait a bit for any animations or dynamic content
                    page.wait_for_timeout(500)
                    
                    # Take screenshot
                    page.screenshot(path=str(output_path), full_page=True)
                    
                except Exception as e:
                    print(f"    WARNING: Failed to render {filename}: {e}", file=sys.stderr)
            
            browser.close()
    
    finally:
        # Shutdown server
        httpd.shutdown()
        print(f"\nScreenshots saved to: {output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Render static HTML pages to PNG screenshots"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("screenshots"),
        help="Output directory for PNG files (default: screenshots)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="Port for local web server (default: 8888)"
    )
    parser.add_argument(
        "--static-dir",
        type=Path,
        default=Path(__file__).parent / "static",
        help="Path to static directory (default: ./static)"
    )
    
    args = parser.parse_args()
    
    # Verify static directory exists
    if not args.static_dir.exists():
        print(f"ERROR: Static directory not found: {args.static_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find HTML files
    html_files = find_html_files(args.static_dir)
    
    if not html_files:
        print(f"ERROR: No HTML files found in {args.static_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(html_files)} HTML files to render:")
    for html_file in html_files:
        print(f"  - {html_file.name}")
    print()
    
    # Render pages
    render_pages_to_png(html_files, args.output_dir, args.port, args.static_dir)


if __name__ == "__main__":
    main()
