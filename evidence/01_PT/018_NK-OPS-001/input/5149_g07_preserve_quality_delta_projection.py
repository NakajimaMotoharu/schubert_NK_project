"""Reversibly archive the one qualified quality-delta text projection."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

location = Path(__file__).with_name("5126_g07_preserve_duplicate_text_projections.py")
spec = spec_from_file_location("projection_retention", location)
retention = module_from_spec(spec)
spec.loader.exec_module(retention)
retention.OUT = retention.EVIDENCE / "PG39432-g07-quality-projection-retention-v1"
retention.REVIEWED = (("PG39430-g07-quality-published-delta-v1", "origins-pass2.json", 1160),)

if __name__ == "__main__":
    retention.main()
