"""New-only complete compile/hash stage. No lock, DB, stop, revoke or Root start is executed."""
import base64
import inspect
import pg4058_original_read_profile as transport
from pg4060_original_profile_dual_stack import once
import pg4088_failed_done_owned_sources as role


def payload():
    values = role.files()
    raw = transport.payload('compile').replace(transport.SLOT, role.TOOLS)
    line = next(line for line in raw.splitlines() if line.startswith('JAVA_B64='))
    raw = once(raw, line, 'JAVA_B64=' + repr(base64.b64encode(values['RootFailedDoneRecovery.java'].encode()).decode()))
    raw = raw.replace('RootOriginalReadProfile.java', 'RootFailedDoneRecovery.java')
    helpers = {n: s for n, s in values.items() if n.endswith('.py')}
    marker = "args=['/opt/jdk-25.0.4/bin/javac'"
    added = 'HELPERS=' + repr(helpers) + "\nfor name,text in HELPERS.items():\n p=save/name;require(p.parent==save and p.suffix=='.py');compile(text,'<frozen recovery helper>','exec');p.write_text(text)\n"
    raw = once(raw, marker, added + marker)
    marker = "(save/'compile.safe.json').write_text(json.dumps(value,sort_keys=True))"
    added = "value['classHashes']={str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')}\nvalue['inputFileHashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [java,annotation,*[save/n for n in HELPERS]]}\nrequire(r.returncode!=0 or bool(value['classHashes']))\nfor p in [java,annotation,*[save/n for n in HELPERS],*classes.rglob('*.class')]:\n os.chmod(p,0o400)\n with p.open('rb')as f:os.fsync(f.fileno())\n"
    return once(raw, marker, added + marker)


def main():
    namespace = {**transport.__dict__, 'payload': lambda action: payload(), 'SLOT': role.TOOLS}
    namespace['sys'] = type('CompileOnlyArguments', (), {'argv': ['compile_stage', 'compile']})
    exec(compile(inspect.getsource(transport.main), '<compile-only complete owned recovery>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
