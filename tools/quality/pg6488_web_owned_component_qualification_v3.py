"""Read original three-phase27; all compiled tests precede any PT; no additional execution."""
import json
from pg6470_web_owned_component_selected import W, BASE, inventory, guard_source, MAIN
from pg6054_expiry_read_qualification import qualify

RUN = W/'pg6486-web-owned-component-v3'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    source = original_source(); cases, _ = inventory()
    return qualify(source, RUN, cases, (27, 11), {MAIN},
        BASE/'PG6468-nio-collision-qualification-v1/manifest.json',
        '6c5e59a7af3d9f88b8b8af6cc8f85346be7d17e1a9e2ab4c89957e2efa432c6e',
        W/'pg6468-nio-collision-qualification-v1/manifest.safe.json',
        W/'pg6468-nio-collision-qualification-v1/findings.safe.json',
        'pg6488-web-owned-component-qualification-v3', 'PG6488-web-owned-component-qualification-v3',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()
