import struct
from dataclasses import dataclass
from typing import BinaryIO


class InvalidImage(ValueError):
    pass


@dataclass(frozen=True)
class ImageInfo:
    mime_type: str
    width: int
    height: int


def detect(stream: BinaryIO) -> ImageInfo:
    stream.seek(0)
    head = stream.read(32)
    if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
        width, height = struct.unpack(">II", head[16:24])
        return ImageInfo("image/png", width, height)
    if head.startswith((b"GIF87a", b"GIF89a")) and len(head) >= 10:
        width, height = struct.unpack("<HH", head[6:10])
        return ImageInfo("image/gif", width, height)
    if head.startswith(b"\xff\xd8"):
        stream.seek(2)
        while True:
            marker_start = stream.read(1)
            if not marker_start:
                break
            if marker_start != b"\xff":
                continue
            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                break
            marker_value = marker[0]
            if marker_value in (0xD8, 0xD9):
                continue
            size_data = stream.read(2)
            if len(size_data) != 2:
                break
            size = struct.unpack(">H", size_data)[0]
            if 0xC0 <= marker_value <= 0xCF and marker_value not in (0xC4, 0xC8, 0xCC):
                payload = stream.read(5)
                if len(payload) != 5:
                    break
                height, width = struct.unpack(">HH", payload[1:5])
                return ImageInfo("image/jpeg", width, height)
            stream.seek(max(size - 2, 0), 1)
    raise InvalidImage("unsupported or malformed image")
