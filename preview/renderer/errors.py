from html import escape
from typing import Optional

from ..domain.contracts import AssetStatus, DiagnosticStage

STATUS_LABELS = {
    AssetStatus.LOADING: "Loading",
    AssetStatus.UNAVAILABLE: "Unavailable",
    AssetStatus.BLOCKED: "Blocked by settings",
    AssetStatus.TOO_LARGE: "Too large",
    AssetStatus.TIMEOUT: "Timed out",
}


def asset_placeholder(status: AssetStatus, privacy: Optional[str] = None) -> str:
    caption = STATUS_LABELS[status]
    detail = "<strong>{}</strong>".format(escape(caption))
    if privacy:
        detail += "<br /><span>{}</span>".format(escape(privacy))
    return '<div class="mdglance-asset-placeholder">{}</div>'.format(detail)


def error_card(stage: DiagnosticStage, message: str) -> str:
    return '<div class="mdglance-error"><strong>{}</strong><br />{}</div>'.format(
        escape(stage.value.title()), escape(message)
    )
