"""New-only read diagnostics after full4052 preserved; no business-state mutation."""
import inspect
import json
from pg1446_current_cold_stage import W
import pg4050_root_unit_read_profile as base


def payload():
    preserved = json.loads((W / 'pg4052-failed-current-capture-v1/manifest.safe.json').read_bytes())
    if preserved['actualExit'] != 0 or preserved['result']['parentFailed143'] is not True:
        raise ValueError('actual preserved failed-current first')
    namespace = {**base.__dict__}
    raw = inspect.getsource(base.payload).replace('RootUnitReadProfile', 'RootFileReadProfile')
    raw = raw.replace('pg4050-unit-read-profile-v1', 'pg4054-file-primitive-profile-v1')
    raw = raw.replace('dev.codex.schubert.nk.batch.platform.', 'dev.codex.schubert.nk.batch.file.')
    exec(compile(raw, '<fixed read-only file primitive diagnostic>', 'exec'), namespace)
    return namespace['payload']()


def main():
    namespace = {**base.__dict__, 'payload': payload}
    raw = inspect.getsource(base.main).replace('pg4050-unit-read-profile-v1', 'pg4054-file-primitive-profile-v1')
    exec(compile(raw, '<new-only profile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
