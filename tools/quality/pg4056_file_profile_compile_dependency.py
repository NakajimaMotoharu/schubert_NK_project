"""BUG1333: new-only corrected diagnostics, pinned compile annotation, no suppression."""
import base64
import hashlib
import inspect
from pathlib import Path
import pg4054_file_primitive_profile as previous
import pg4050_root_unit_read_profile as transport

JAR = Path('/home/mini/codex/project1/work/toolchain/m2/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar')
SHA = '28fa4befaddce5d7b79b07c68e7c12fa27c5d9282c4229528717971606661ea3'
SLOT = 'pg4056-file-primitive-profile-v1'


def dependency(path=JAR):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('fixed compile annotation bytes required')
    return raw


def payload():
    raw = previous.payload().replace('pg4054-file-primitive-profile-v1', SLOT)
    marker = "env={k:v for k,v in os.environ.items()"
    if raw.count(marker) != 1: raise ValueError('one explicit compile dependency boundary')
    added = "import base64\nannotation=out/'spotbugs-annotations-4.10.4.jar'\nannotation_raw=base64.b64decode(" + repr(base64.b64encode(dependency()).decode()) + ")\nassert hashlib.sha256(annotation_raw).hexdigest()==" + repr(SHA) + "\nannotation.write_bytes(annotation_raw)\ncp+=':'+str(annotation)\n"
    raw = raw.replace(marker, added + marker)
    compile(raw, '<new-only pinned annotation diagnostic>', 'exec')
    return raw


def main():
    namespace = {**transport.__dict__, 'payload': payload}
    raw = inspect.getsource(transport.main).replace('pg4050-unit-read-profile-v1', SLOT)
    exec(compile(raw, '<new corrected dependency profile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
