"""
Browser interaction utilities.
"""

import webbrowser


def open_url(url: str):
    """Open given URL in default web browser."""
    if url:
        try:
            webbrowser.open(url)
        except Exception:
            pass
