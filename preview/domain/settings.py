from typing import Any, Callable, Mapping, Optional

from .contracts import RenderSettings


def _number(
    values: Mapping[str, Any],
    key: str,
    default: Any,
    minimum: float,
    maximum: float,
    integer: bool,
    warn: Callable[[str], None],
) -> Any:
    value = values.get(key, default)
    expected = int if integer else (int, float)
    if isinstance(value, bool) or not isinstance(value, expected):
        warn("Invalid setting {!r}; using default".format(key))
        return default
    value = max(minimum, min(maximum, value))
    return int(value) if integer else float(value)


def _boolean(
    values: Mapping[str, Any],
    key: str,
    default: bool,
    warn: Callable[[str], None],
) -> bool:
    value = values.get(key, default)
    if not isinstance(value, bool):
        warn("Invalid setting {!r}; using default".format(key))
        return default
    return value


def parse_settings(
    values: Mapping[str, Any], warn: Optional[Callable[[str], None]] = None
) -> RenderSettings:
    report = warn or (lambda message: None)
    defaults = RenderSettings()
    server = values.get("mermaid_server", defaults.mermaid_server)
    if not isinstance(server, str) or not server.startswith("https://"):
        report("Invalid setting 'mermaid_server'; using default")
        server = defaults.mermaid_server
    return RenderSettings(
        update_delay_ms=_number(
            values, "update_delay_ms", defaults.update_delay_ms, 0, 5000, True, report
        ),
        enable_mermaid=_boolean(
            values, "enable_mermaid", defaults.enable_mermaid, report
        ),
        mermaid_server=server.rstrip("/"),
        allow_insecure_remote_images=_boolean(
            values,
            "allow_insecure_remote_images",
            defaults.allow_insecure_remote_images,
            report,
        ),
        remote_timeout_seconds=_number(
            values,
            "remote_timeout_seconds",
            defaults.remote_timeout_seconds,
            1,
            120,
            False,
            report,
        ),
        remote_max_bytes=_number(
            values,
            "remote_max_bytes",
            defaults.remote_max_bytes,
            1024,
            100 * 1024 * 1024,
            True,
            report,
        ),
        remote_max_dimension=_number(
            values,
            "remote_max_dimension",
            defaults.remote_max_dimension,
            16,
            32768,
            True,
            report,
        ),
        table_max_columns=_number(
            values,
            "table_max_columns",
            defaults.table_max_columns,
            8,
            400,
            True,
            report,
        ),
        toc_minimum_length=_number(
            values,
            "toc_minimum_length",
            defaults.toc_minimum_length,
            0,
            10 * 1024 * 1024,
            True,
            report,
        ),
        toc_minimum_headings=_number(
            values,
            "toc_minimum_headings",
            defaults.toc_minimum_headings,
            0,
            10000,
            True,
            report,
        ),
        debug_logging=_boolean(values, "debug_logging", defaults.debug_logging, report),
    )
