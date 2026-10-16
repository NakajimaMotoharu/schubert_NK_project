"""New observation window of original Root; previous4610 evidence is immutable."""
import json
import pg4610_current_parent_progress_read as previous
from pg1446_current_cold_stage import W

SLOT='pg4618-current-parent-progress-read-v1'


def main():
    rows=[json.loads(line)for line in(W/'pg4560-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    expected=previous.cost.previous.parent.select_parent(rows)
    return previous.admission.execute(SLOT,previous.payload(expected).replace(previous.SLOT,SLOT))


if __name__=='__main__':raise SystemExit(main())
