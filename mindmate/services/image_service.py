import json
import ssl
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi


class ImageSearchError(Exception):
    """Raised when Wikimedia Commons cannot be searched."""


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def _plain_text(value: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(value)
    return " ".join(extractor.parts)


def search_commons_images(topic: str, limit: int = 4) -> list[dict[str, str]]:
    """Find reusable Wikimedia Commons images and the details needed to credit them."""
    params = urlencode(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": 6,
            "gsrsearch": f"filetype:bitmap {topic}",
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 800,
        }
    )
    request = Request(
        f"https://commons.wikimedia.org/w/api.php?{params}",
        headers={"User-Agent": "MindMateLearningApp/1.0 (educational use)"},
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=8, context=ssl_context) as response:
            data = json.loads(response.read())
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ImageSearchError(f"Wikimedia Commons image search failed: {error}") from error

    pages = data.get("query", {}).get("pages", {})
    images = []
    for page in pages.values():
        image_info = (page.get("imageinfo") or [{}])[0]
        metadata = image_info.get("extmetadata", {})
        thumbnail_url = image_info.get("thumburl", "")
        source_url = image_info.get("descriptionurl", "")
        trusted_thumbnail = thumbnail_url.startswith(
            ("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")
        )
        if not trusted_thumbnail or not source_url.startswith("https://commons.wikimedia.org/"):
            continue

        images.append(
            {
                "title": page.get("title", "Wikimedia Commons image"),
                "thumbnail_url": thumbnail_url,
                "source_url": source_url,
                "artist": _plain_text(metadata.get("Artist", {}).get("value", "Not listed")),
                "license": metadata.get("LicenseShortName", {}).get("value", "Check source page"),
            }
        )
    return images
