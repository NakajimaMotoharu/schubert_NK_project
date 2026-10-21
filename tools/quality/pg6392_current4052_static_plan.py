"""Reauthenticate current1355 before whole-case join; no old semantic success transfer."""
import inspect
import json
import os
import pg6308_current4043_static_plan as prior
from pg6384_web_fatal_callback_retry_qualification import original_source

PRIOR = prior.BASE/'PG6362-systemd-cgroup-static-review-v1/manifest.json'
PRIOR_SHA = '558673dec3399b54cd6525aa777867fe1a84dac93dac3c88c4cf7fa56dc8acc3'
OLD = 'aed19c6dca368e9717309d6f744d7917c6b7b32c'


def calculate():
    scope = {**vars(prior), 'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'original_source': original_source}
    raw = inspect.getsource(prior.calculate)
    for before, after in (
        ('PG6298-web-send-qualification-v1', 'PG6384-web-fatal-callback-retry-qualification-v1'),
        ('pg6298-web-send-qualification-v1', 'pg6384-web-fatal-callback-retry-qualification-v1'),
        ('00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27', '7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7'),
        ('PG6272-current4040-cases', 'PG6330-current4048-cases'),
        ('dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5', '2b57d476af5f0d0e29c9b706220ba2f0c54ac8d2c4c22aac0685f45da14598d3'),
        ('1357', '1355'), ('selected84', 'selected22')):
        if before not in raw:
            raise ValueError('explicit current1355 source/static binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<current1355 strict source-class reauthentication>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077)
    out = prior.BASE/'PG6392-current4052-static-plan-v1'; out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(rows, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value['inventorySha256'] = prior.sha(out/'findings.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=value['source'], statusCounts=value['statusCounts'],
        strictReboundPriorDecided=value['strictReboundPriorDecided'], priorUnresolvedRetained=14,
        manifestSha256=prior.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
