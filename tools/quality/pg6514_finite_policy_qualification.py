"""Original6512 XML/Jars only; all851 Main and all1667 physical bytes unchanged."""
import json
from pg6512_finite_policy_factories import W, BASE, SLOT, inventory, guard_source
from pg6054_expiry_read_qualification import qualify

RUN = W/SLOT


def main():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    cases, _ = inventory()
    return qualify(source, RUN, cases, (20, 8), set(),
        BASE/'PG6500-web-owned-component-qualification-v5/manifest.json',
        '67be969bc999b8cc5cd020faea6f1604bf8c32ebf8673f6db4a13910a8e90722',
        W/'pg6500-web-owned-component-qualification-v5/manifest.safe.json',
        W/'pg6500-web-owned-component-qualification-v5/findings.safe.json',
        'pg6514-finite-policy-qualification-v1', 'PG6514-finite-policy-qualification-v1',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()
