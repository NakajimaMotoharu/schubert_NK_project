"""Original fresh23 all artifacts; no older diagnostic run imported as current PT."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6448_morning_sequence_green import inventory, guard_source, MAIN

RUN = W/'pg6448-morning-sequence-green-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (23, 10), {MAIN},
        BASE/'PG6442-morning-diagnostic-qualification-v1/manifest.json',
        '0a1a830e54043d67f1ace8abb61aedc008eaa3431517719ecabcd8589400f3ff',
        W/'pg6442-morning-diagnostic-qualification-v1/manifest.safe.json',
        W/'pg6442-morning-diagnostic-qualification-v1/findings.safe.json',
        'pg6450-morning-sequence-qualification-v1', 'PG6450-morning-sequence-qualification-v1')


if __name__ == '__main__':
    main()
