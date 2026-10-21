"""Original6516 XML/Jars only; unchanged Production and gates, no native qualification."""
import json
from pg6516_caddy_identity_literals import W, BASE, SLOT, inventory, guard_source
from pg6054_expiry_read_qualification import qualify

RUN = W/SLOT


def main():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    cases, _ = inventory()
    return qualify(source, RUN, cases, (15, 8), set(),
        BASE/'PG6514-finite-policy-qualification-v1/manifest.json',
        '2664499fdf336a41910917a9392091abc86bcc7ba4f2f081de0de7553c58db5f',
        W/'pg6514-finite-policy-qualification-v1/manifest.safe.json',
        W/'pg6514-finite-policy-qualification-v1/findings.safe.json',
        'pg6518-caddy-identity-qualification-v1', 'PG6518-caddy-identity-qualification-v1',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()
