"""Write the checksum inventory for an already written PGPT scope manifest."""
from hashlib import sha256
from pathlib import Path


def write_scope_checksums(directory, files):
    """Bind the manifest and its declared files without rescanning the directory."""
    manifest = directory / "manifest.json"
    entries = [(Path(entry["path"]), entry["sha256"]) for entry in files]
    entries.append((Path(manifest.name), sha256(manifest.read_bytes()).hexdigest()))
    (directory / "checksums.sha256").write_text(
        "".join(f"{digest}  {path}\n" for path, digest in sorted(entries)),
        encoding="utf-8",
    )
