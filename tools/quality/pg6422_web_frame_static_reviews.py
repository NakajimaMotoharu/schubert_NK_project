"""Five current borrowed-frame source spans, never real-runtime or whole success."""
import inspect
import json
import os
import pg6394_startup_static_reviews as engine
from pg6414_web_frame_pending_qualification import original_source

G = engine.G
SPEC = {'WebRuntimeExecution': {
    (46, G): (2, 'Both Runtime/Error from the sole close attempt, together with typed IOException, retain the same borrowed callback frame rather than report normal cleanup. The fixed prepared diagnostic and protected finite tick precede five reachability fences inside both javac finally clones. Original normal/null/primary exception behavior remains separate and tested; arbitrary stop callback/VM fatal failures are not claimed safe.'),
    (64, 'EmptyCatchBlock'): (1, 'A failed fixed WEB cleanup diagnostic is contained solely to preserve UNKNOWN, not treated as successful print/release. The original outer frame keeps its callbacks and close failure alive and never retries cleanup; the fixed literal cannot disclose provider data.'),
    (64, G): (2, 'Both unchecked fixed diagnostic failures are contained before returning to the caller-owned holding loop. No new raw failure graph, normal receipt or downstream close is produced. Normal and exceptional finally inputs are distinct original26 actual cases and must still join the current whole before F03 acceptance.')
}}
TESTS = {'WebRuntimeExecution': ['web.bootstrap.WebRuntimeExecutionTest',
    'web.bootstrap.WebRuntimeExecutionRetentionTest', 'web.bootstrap.WebRuntimePendingFailureRetentionTest']}


def calculate():
    scope = {**vars(engine), 'SPEC': SPEC, 'TESTS': TESTS, 'original_source': original_source,
        'PLAN': engine.BASE/'PG6418-current4054-static-plan-v1/manifest.json',
        'PLAN_SHA': 'a1a47acc908d16177bbc6614e48519ba4c90b10e2c11e8160580fd10b95cf804'}
    raw = inspect.getsource(engine.calculate)
    for before, after in (
        ('PG6384-web-fatal-callback-retry-qualification-v1', 'PG6414-web-frame-pending-qualification-v1'),
        ('pg6384-web-fatal-callback-retry-qualification-v1', 'pg6414-web-frame-pending-qualification-v1'),
        ('7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7', 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f'),
        ('len(decisions) != 19', 'len(decisions) != 5'), ('all19 individually', 'all5 individually'),
        ('reviewed=19', 'reviewed=5'), ('rawFindings=1355', 'rawFindings=1358'),
        ('161 other current', '134 other current'), ('current4052 whole', 'current4054 whole')):
        if before not in raw:
            raise ValueError('explicit current1358/five-span binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<five current frame applicability spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = engine.BASE/'PG6422-web-frame-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=5, statusCounts=value['statusCounts'], manifestSha256=engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
