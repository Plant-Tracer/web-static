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
            
            # Define viewports for desktop and mobile
            viewports = [
                {"name": "desktop", "width": 1280, "height": 720},
                {"name": "mobile", "width": 590, "height": 720},
            ]

            for viewport in viewports:
                viewport_name = viewport["name"]
                viewport_width = viewport["width"]
                viewport_height = viewport["height"]

                print(f"\nRendering pages for {viewport_name} viewport ({viewport_width}x{viewport_height})")

                # Create a new page with the specified viewport
                page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})

                for html_file in html_files:
                    filename = html_file.name
                    
                    if filename == "usingplanttracerwebapp.html":
                        # Skip the webapp specific page for this rendering (for now)
                        continue

                    stem = html_file.stem
                    output_filename = f"{stem}-{viewport_name}.png"
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

                        # Special handling for usingplanttracerios.html on desktop
                        if viewport_name == "desktop" and filename == "usingplanttracerios.html":
                            print(f"    Capturing substeps for {filename}")

                            # Get all substep elements
                            substeps = page.query_selector_all(".desktop .bigSubStep")
                            num_substeps = len(substeps)

                            # Loop through substeps and capture each state
                            for i in range(num_substeps - 1):
                                # Find the visible next button and click it
                                next_button = page.locator(".desktop .bigSubStep[style*='display: flex;'] .nextBtn")

                                try:
                                    next_button.click()
                                except Exception as e:
                                    print(f"      WARNING: Could not find or click next button on substep {i+1}: {e}", file=sys.stderr)
                                    break

                                # Wait for transition
                                page.wait_for_timeout(500)

                                # Define substep output path
                                substep_filename = f"{html_file.stem}-{viewport_name}-substep-{i + 2:03d}.png"
                                substep_output_path = output_dir / substep_filename

                                print(f"      Rendering substep {i + 2} -> {substep_filename}")

                                # Take screenshot of the substep
                                page.screenshot(path=str(substep_output_path), full_page=True)

                        # Special handling for usingplanttracerios.html on mobile
                        elif viewport_name == "mobile" and filename == "usingplanttracerios.html":
                            print(f"    Capturing mobile substeps for {filename}")

                            # Get all mobile substep elements
                            substeps = page.query_selector_all(".Mobile .mobileStep")
                            num_substeps = len(substeps)

                            # Loop through substeps and capture each state
                            for i in range(num_substeps - 1):
                                # Find the mobile next button and click it
                                next_button = page.locator(".Mobile .buttons .nextBtn")

                                try:
                                    next_button.click()
                                except Exception as e:
                                    print(f"      WARNING: Could not find or click mobile next button on substep {i+1}: {e}", file=sys.stderr)
                                    break

                                # Wait for transition
                                page.wait_for_timeout(500)

                                # Define substep output path
                                substep_filename = f"{html_file.stem}-{viewport_name}-substep-{i + 2:03d}.png"
                                substep_output_path = output_dir / substep_filename

                                print(f"      Rendering mobile substep {i + 2} -> {substep_filename}")

                                # Take screenshot of the substep
                                page.screenshot(path=str(substep_output_path), full_page=True)


                    except Exception as e:
                        print(f"    WARNING: Failed to render {filename}: {e}", file=sys.stderr)

                page.close()

            
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
