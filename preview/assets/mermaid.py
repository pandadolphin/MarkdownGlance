import base64
import json


def mermaid_image_url(diagram: str, server: str) -> str:
    payload = json.dumps(
        {"code": diagram, "mermaid": {"theme": "default"}},
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return "{}/img/{}?type=png".format(server.rstrip("/"), encoded)
