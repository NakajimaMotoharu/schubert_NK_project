"""Current1358 source/physical reauthentication, no old case success import."""
import inspect
import json
import os
import pg6308_current4043_static_plan as prior
from pg6414_web_frame_pending_qualification import original_source

PRIOR = prior.BASE/'PG6406-current4052-static-join-v1/manifest.json'
PRIOR_SHA = '339d88494b3b28c110280cce2dee7cee09dc5c1c5897fa2082a287a3ddb4bdbd'
OLD = 'c34159083bfec296fd929ec9b2fbdbb80831c05c'


def calculate():
    scope = {**vars(prior), 'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'original_source': original_source}
    raw = inspect.getsource(prior.calculate)
    for before, after in (
        ('PG6298-web-send-qualification-v1', 'PG6414-web-frame-pending-qualification-v1'),
        ('pg6298-web-send-qualification-v1', 'pg6414-web-frame-pending-qualification-v1'),
        ('00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27', 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f'),
        ('PG6272-current4040-cases', 'PG6386-current4052-cases'),
        ('dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5', '5b42051bf7ca435c44e3f7caa2fb0fca245faae9c32c3fda4b508ee40a4314b4'),
        ('1357', '1358'), ('selected84', 'selected26')):
        if before not in raw:
            raise ValueError('explicit current1358 source/static binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<current1358 strict source-class reauthentication>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = prior.BASE/'PG6418-current4054-static-plan-v1'; out.mkdir()
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
