"""Read original supplementary26; all Main must equal original25, no PT success import."""
import json
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6412_web_frame_pending_selected import inventory, guard_source

RUN = W/'pg6412-web-frame-pending-selected-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source)
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (26, 12), set(),
        BASE/'PG6400-web-frame-qualification-v1/manifest.json',
        '59792d63765ca0713feebe147b225a82e3319f72984218d6940b43e198288ca3',
        W/'pg6400-web-frame-qualification-v1/manifest.safe.json',
        W/'pg6400-web-frame-qualification-v1/findings.safe.json',
        'pg6414-web-frame-pending-qualification-v1', 'PG6414-web-frame-pending-qualification-v1')


if __name__ == '__main__':
    main()
