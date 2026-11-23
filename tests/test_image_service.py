import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import URLError

from mindmate.services.image_service import ImageSearchError, search_commons_images


class SearchCommonsImagesTests(unittest.TestCase):
    @patch("mindmate.services.image_service.urlopen")
    def test_returns_image_and_attribution_details(self, mocked_urlopen):
        response_data = {
            "query": {
                "pages": {
                    "123": {
                        "title": "File:Example image.jpg",
                        "imageinfo": [
                            {
                                "thumburl": "https://thumb.wikimedia.org/example.jpg",
                                "descriptionurl": "https://commons.wikimedia.org/wiki/File:Example_image.jpg",
                                "extmetadata": {
                                    "Artist": {"value": '<a href="/wiki/User:Example">Example artist</a>'},
                                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                },
                            }
                        ],
                    }
                }
            }
        }
        mocked_urlopen.return_value = BytesIO(json.dumps(response_data).encode())

        images = search_commons_images("photosynthesis")

        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["artist"], "Example artist")
        self.assertEqual(images[0]["license"], "CC BY-SA 4.0")
        self.assertEqual(images[0]["title"], "File:Example image.jpg")

    @patch("mindmate.services.image_service.urlopen")
    def test_ignores_images_outside_wikimedia_hosts(self, mocked_urlopen):
        response_data = {
            "query": {
                "pages": {
                    "123": {
                        "title": "File:Untrusted image.jpg",
                        "imageinfo": [
                            {
                                "thumburl": "https://example.com/image.jpg",
                                "descriptionurl": "https://example.com/source",
                            }
                        ],
                    }
                }
            }
        }
        mocked_urlopen.return_value = BytesIO(json.dumps(response_data).encode())

        self.assertEqual(search_commons_images("photosynthesis"), [])

    @patch("mindmate.services.image_service.urlopen", side_effect=URLError("offline"))
    def test_reports_network_failure(self, _mocked_urlopen):
        with self.assertRaises(ImageSearchError):
            search_commons_images("photosynthesis")


if __name__ == "__main__":
    unittest.main()
