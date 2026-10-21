"""Read new18 original XML/Jars and allowed static; no additional PT or Production execution."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6348_web_lifetime_selected import inventory, guard_source

RUN = W/'pg6348-web-lifetime-selected-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (18, 9), set(),
        BASE/'PG6326-web-graph-qualification-v1/manifest.json',
        'e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf',
        W/'pg6326-web-graph-qualification-v1/manifest.safe.json',
        W/'pg6326-web-graph-qualification-v1/findings.safe.json',
        'pg6350-web-lifetime-qualification-v1', 'PG6350-web-lifetime-qualification-v1')


if __name__ == '__main__':
    main()
