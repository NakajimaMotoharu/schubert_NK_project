"""Readonly actual new Source Root binding; never start/stop/replay authority."""
import inspect
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'vm/050_s1'))
import pg1321_live_root_binding as prior

SOURCE = '2741c4546afad6c1e8b6efbd53dfb58144edf7bb'
DIGEST = '195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'


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
    ns = {**prior.__dict__, 'BODY': body(), 'SOURCE': SOURCE, 'DIGEST': DIGEST}
    exec(compile(raw, '<new Source readonly transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
