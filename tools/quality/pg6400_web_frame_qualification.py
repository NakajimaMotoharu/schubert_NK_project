"""Qualify genuine25/all8511667/sixJar and actual borrowed-frame counters, never run PT."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6398_web_frame_green import inventory, guard_source, MAIN

RUN = W/'pg6398-web-frame-green-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (25, 11), {MAIN},
        BASE/'PG6384-web-fatal-callback-retry-qualification-v1/manifest.json',
        '7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7',
        W/'pg6384-web-fatal-callback-retry-qualification-v1/manifest.safe.json',
        W/'pg6384-web-fatal-callback-retry-qualification-v1/findings.safe.json',
        'pg6400-web-frame-qualification-v1', 'PG6400-web-frame-qualification-v1')


if __name__ == '__main__':
    main()
