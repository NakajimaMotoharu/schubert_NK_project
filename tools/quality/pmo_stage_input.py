"""Pure checkpoint input checks before any group event or persistent state mutation.

BUG3006/YKT2535; WBS-F03; PT-OPS-ENDINPUT001..012. No file or process access.
"""


def validate_checkpoint_text(mode: str, config: object) -> str | None:
    """Preserve the exact nonblank end text; start records do not require it."""
    if mode not in ("start", "end"):
        raise ValueError("registered stage mode required")
    if not isinstance(config, dict):
        raise ValueError("stage config object required")
    if mode == "start":
        return None
    value = config.get("checkpointText")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonblank end checkpointText required before mutation")
    return value
