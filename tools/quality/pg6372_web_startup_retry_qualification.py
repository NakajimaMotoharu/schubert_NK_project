"""Original corrected54 XML/Jars/static; two Main differ only from prior qualified18."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6364_web_startup_green import MAIN
from pg6370_web_startup_retry import inventory, guard_source

RUN = W/'pg6370-web-startup-retry-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (54, 15), MAIN,
        BASE/'PG6350-web-lifetime-qualification-v1/manifest.json',
        'fb7279b4a9133049b535475703d2eb52f76c7f9c2c5fc040a2c25369fb7d3b71',
        W/'pg6350-web-lifetime-qualification-v1/manifest.safe.json',
        W/'pg6350-web-lifetime-qualification-v1/findings.safe.json',
        'pg6372-web-startup-retry-qualification-v1', 'PG6372-web-startup-retry-qualification-v1')


if __name__ == '__main__':
    main()
