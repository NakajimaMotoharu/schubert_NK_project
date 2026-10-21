"""Read only original6480/27 current all-Main artifacts; never executes old/new PT."""
import json
from pg6470_web_owned_component_selected import W, BASE, inventory, guard_source, MAIN
from pg6054_expiry_read_qualification import qualify

RUN = W/'pg6480-web-owned-component-v2'


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
        'pg6482-web-owned-component-qualification-v2', 'PG6482-web-owned-component-qualification-v2')


if __name__ == '__main__':
    main()
