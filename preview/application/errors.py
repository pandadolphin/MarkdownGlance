from ..domain.contracts import DiagnosticStage


class RenderFailure(Exception):
    def __init__(self, stage: DiagnosticStage, message: str) -> None:
        super().__init__(message)
        self.stage = stage
        self.safe_message = message
