"""Read original23 all sources/Jars/XML, then existing analyzers only; no PT/build rerun."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6440_morning_diagnostic_green import inventory, guard_source, MAIN

RUN = W/'pg6440-morning-diagnostic-green-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (23, 10), {MAIN},
        BASE/'PG6414-web-frame-pending-qualification-v1/manifest.json',
        'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f',
        W/'pg6414-web-frame-pending-qualification-v1/manifest.safe.json',
        W/'pg6414-web-frame-pending-qualification-v1/findings.safe.json',
        'pg6442-morning-diagnostic-qualification-v1', 'PG6442-morning-diagnostic-qualification-v1')


if __name__ == '__main__':
    main()
