"""Read original22 same-Main XML/Jars and permitted static; no additional PT or native action."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6376_web_fatal_callback_selected import inventory, guard_source

RUN = W/'pg6376-web-fatal-callback-selected-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (22, 8), set(),
        BASE/'PG6372-web-startup-retry-qualification-v1/manifest.json',
        '2a9e57d2a1da1ca2520af978526b0fc9b5f1b1081678f9dfe6481823e1f494d3',
        W/'pg6372-web-startup-retry-qualification-v1/manifest.safe.json',
        W/'pg6372-web-startup-retry-qualification-v1/findings.safe.json',
        'pg6378-web-fatal-callback-qualification-v1', 'PG6378-web-fatal-callback-qualification-v1')


if __name__ == '__main__':
    main()
