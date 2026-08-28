import io
import socket
import unittest
from unittest.mock import patch

from MarkdownGlance.preview.assets.fetcher import ImageFetcher, _RedirectHandler
from MarkdownGlance.preview.assets.policy import NetworkPolicy
from MarkdownGlance.preview.domain.contracts import (
    AssetKey,
    AssetKind,
    AssetStatus,
    Failed,
    Ready,
    RenderSettings,
)

PNG = (
    b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + b"\x00\x00\x00\x01\x00\x00\x00\x02" + b"x" * 8
)


class Response(io.BytesIO):
    def __init__(self, content, url="https://example.test/image", length=None):
        super().__init__(content)
        self._url = url
        self.headers = {}
        if length is not None:
            self.headers["Content-Length"] = str(length)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def geturl(self):
        return self._url


class Opener:
    def __init__(self, response):
        self.response = response

    def open(self, request, timeout):
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class FetcherTest(unittest.TestCase):
    def setUp(self):
        self.key = AssetKey(AssetKind.REMOTE_IMAGE, "https://example.test/image")

    def fetch(self, response, settings=RenderSettings()):
        with patch(
            "MarkdownGlance.preview.assets.fetcher.urllib.request.build_opener",
            return_value=Opener(response),
        ):
            return ImageFetcher().fetch(self.key, NetworkPolicy(settings))

    def test_success_uses_signature_and_effective_scheme(self):
        result = self.fetch(Response(PNG))
        self.assertIsInstance(result, Ready)
        self.assertEqual((result.asset.width, result.asset.height), (1, 2))
        self.assertEqual(result.asset.effective_scheme, "https")

    def test_declared_and_streamed_oversize_are_rejected(self):
        settings = RenderSettings(remote_max_bytes=1024)
        declared = self.fetch(Response(PNG, length=2048), settings)
        streamed = self.fetch(Response(PNG * 40), settings)
        self.assertEqual(declared, Failed(AssetStatus.TOO_LARGE))
        self.assertEqual(streamed, Failed(AssetStatus.TOO_LARGE))

    def test_timeout_and_invalid_payload_are_typed_failures(self):
        self.assertEqual(self.fetch(socket.timeout()), Failed(AssetStatus.TIMEOUT))
        self.assertEqual(
            self.fetch(Response(b"not an image")), Failed(AssetStatus.UNAVAILABLE)
        )

    def test_https_downgrade_redirect_is_blocked(self):
        handler = _RedirectHandler(False)
        request = type("Request", (), {"full_url": "https://example.test/a"})()
        with self.assertRaises(PermissionError):
            handler.redirect_request(
                request, None, 302, "Found", {}, "http://example.test/b"
            )


if __name__ == "__main__":
    unittest.main()
