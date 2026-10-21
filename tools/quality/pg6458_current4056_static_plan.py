"""Current1361 source/class reauthentication; exactly12 prior semantic gaps remain held."""
import inspect
import json
import os
import pg6308_current4043_static_plan as prior
from pg6450_morning_sequence_qualification import original_source

PRIOR = prior.BASE/'PG6432-control-client-static-review-v1/manifest.json'
PRIOR_SHA = '117fd6ab8314b631e762bb7a775b43f0f4ac0860f6a85ad775310676a395ae71'
OLD = '669ad5fd83f67ad031b2c1734d7fc5716599d35d'


def calculate():
    scope = {**vars(prior), 'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'original_source': original_source}
    raw = inspect.getsource(prior.calculate)
    for before, after in (
        ('PG6298-web-send-qualification-v1', 'PG6450-morning-sequence-qualification-v1'),
        ('pg6298-web-send-qualification-v1', 'pg6450-morning-sequence-qualification-v1'),
        ('00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27', '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0'),
        ('PG6272-current4040-cases', 'PG6408-current4054-cases'),
        ('dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5', '2fe8efc5bc8ad1c60487a1366ba80c159fe8c61cf937fd2509b8d4298591b0a7'),
        ('1357', '1361'), ('selected84', 'selected23'), ('held!=14', 'held!=12'),
        ('all fourteen unresolved', 'all twelve unresolved')):
        if before not in raw:
            raise ValueError('explicit current1361/all12 held binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<current1361 strict source-class reauthentication>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = prior.BASE/'PG6458-current4056-static-plan-v1'; out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(rows, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value['inventorySha256'] = prior.sha(out/'findings.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=value['source'], statusCounts=value['statusCounts'],
        strictReboundPriorDecided=value['strictReboundPriorDecided'], priorUnresolvedRetained=12,
        manifestSha256=prior.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
