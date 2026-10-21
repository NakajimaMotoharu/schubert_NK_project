"""Read original13 artifacts only; all Main/Jar/PMD bytes remain independently bound."""
import json
from pg6466_nio_collision_selected import W, BASE, inventory, guard_source
from pg6054_expiry_read_qualification import qualify

RUN = W/'pg6466-nio-collision-selected-v1'


def main():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source); cases, _ = inventory()
    return qualify(source, RUN, cases, (13, 8), set(),
        BASE/'PG6450-morning-sequence-qualification-v1/manifest.json',
        '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0',
        W/'pg6450-morning-sequence-qualification-v1/manifest.safe.json',
        W/'pg6450-morning-sequence-qualification-v1/findings.safe.json',
        'pg6468-nio-collision-qualification-v1', 'PG6468-nio-collision-qualification-v1')


if __name__ == '__main__':
    main()
