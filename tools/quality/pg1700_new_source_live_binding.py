"""Readonly actual new Source Root binding; never start/stop/replay authority."""
import inspect
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'vm/050_s1'))
import pg1321_live_root_binding as prior

SOURCE = '2741c4546afad6c1e8b6efbd53dfb58144edf7bb'
DIGEST = '195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'


def captured_parent(start, before):
    if (type(start) is not dict or start.get('actualExit') != 0
            or type(before) is not dict or before.get('actualExit') != 0
            or before.get('productionSource') != SOURCE
            or before.get('whole187SignedArtifactBytesVerified') is not True
            or before.get('newSourceParentNotStarted') is not True
            or start.get('payloadSha256') != 'e38ba715fc03defe5f67b4032df33e73cf8641afeea88bbdc5ea2bca97020805'):
        raise ValueError('actual successful once envelope required')
    parent = start.get('guest')
    expected = dict(MainPID='302199', InvocationID='fe43e94b1fbf4886bb4ab3922fd16f9c',
                    Job='106924', ExecMainStartTimestampMonotonic='66941284515')
    if type(parent) is not dict or any(parent.get(k) != v for k, v in expected.items()):
        raise ValueError('actual captured four-field Root identity required')
    if parent.get('clientExit') != 0 or parent.get('ordinaryNoargs') is not True or parent.get('originalBudgetSeconds') != 1800:
        raise ValueError('ordinary start receipt contract required')
    return expected


def body():
    raw = prior.BODY.replace('cbca8738-3b24-4090-b77c-bf029677cdd6',
                             '3d69f5af-6bac-46b1-a540-7591c4a79a0d')
    raw = raw.replace('cbca87383b244090b77cbf029677cdd6',
                      '3d69f5af6bac46b1a5407591c4a79a0d')
    raw = raw.replace('0.1.0-PG1292', '0.1.0-PG1638')
    compile(raw, '<new Source live readonly binding>', 'exec')
    return raw


def main():
    raw = inspect.getsource(prior.main)
    raw = raw.replace('pg1320-published-ordinary-once-v1.safe.json',
                      'pg1699-new-current-ordinary-once-v1/manifest.safe.json')
    raw = raw.replace('pg1321-live-root-binding-v1', 'pg1700-new-source-live-binding-v1')
    old = "if start['actualExit']!=0 or start['productionSource']!=SOURCE or not start['externalStartIssuedOnce']:raise ValueError('actual once start required')"
    if raw.count(old) != 1:
        raise ValueError('single legacy schema join required')
    raw = raw.replace(old, "expected=captured_parent(start, json.loads((W/'pg1697-new-current-ordinary-before-v1/manifest.safe.json').read_bytes()))")
    raw = raw.replace("repr(start['parent'])", 'repr(expected)')
    ns = {**prior.__dict__, 'BODY': body(), 'SOURCE': SOURCE, 'DIGEST': DIGEST,
          'captured_parent': captured_parent, 'json': json}
    exec(compile(raw, '<new Source readonly transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
