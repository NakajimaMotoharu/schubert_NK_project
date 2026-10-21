"""Original6520 artifacts only; unchanged851Main/1667physical/sixJar qualification."""
import json
from pg6520_maintenance_owner_selected import W, BASE, SLOT, Q, QSHA, inventory, guard_source
from pg6054_expiry_read_qualification import qualify


def main():
    run = W/SLOT
    source = json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    cases, _ = inventory()
    return qualify(source, run, cases, (15, 8), set(), Q, QSHA,
        W/'pg6518-caddy-identity-qualification-v1/manifest.safe.json',
        W/'pg6518-caddy-identity-qualification-v1/findings.safe.json',
        'pg6522-maintenance-owner-qualification-v1', 'PG6522-maintenance-owner-qualification-v1',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()
