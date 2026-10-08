"""SSC230 new-only Root stage and one completed retirement; no start/stop.

Rebind the previously executed immutable transport, not its old operation slot.
All textual bindings are counted, independently tested and fail closed.
"""
from pathlib import Path

R = Path(__file__).resolve().parent


def source():
    raw = (R/'pg635_resume_native.py').read_text()
    replacements = (
        ("('stage','prepare')", "('stage','retire')"),
        ("PREFIXES=['pg635-resume-tools-v1'", "PREFIXES=['pg647-retirement-tools-v1','pg642-native-tools-v1'"),
        ("HOST_PREFIXES=['pg633-pending-tools-v2'", "HOST_PREFIXES=['pg642-native-tools-v1','pg633-pending-tools-v2'"),
        ("oracle=(W/'pg635-oracle-v2.private.log').read_text()\n    assert oracle.count('\\nOK\\n')==1 and 'FAILED'not in oracle and 'PG635_INDEPENDENT_CLI actual0=true authority0=true' in oracle",
         "assert (W/'pg647-cli-v1.private.log').read_bytes()==b'PG647_INDEPENDENT_CLI actual0=true authority0=true\\n'\n    build=json.loads((W/'pg647-build-v1.safe.json').read_bytes());assert build['compileExit']==build['cliExit']==0\n    for name,sha in build['files'].items():assert hashlib.sha256((W/'pg647-retirement-tools-v1'/name).read_bytes()).hexdigest()==sha"),
        ("('pg635_resume_contract.py','pg635_resume_refs.py','pg633_pending_contract.py','pg604_unit_sources.py','pg629_failed_receipt.py')",
         "('pg647_retirement_contract.py','pg647_runtime_retirement_refs.py','pg646_completed_baseline.py','pg635_resume_contract.py','pg633_pending_contract.py','pg604_unit_sources.py')"),
        ("('Pg464CodeOnlyDeployment.class'", "('Pg642NativeStop.class','Pg642NativeStop$References.class','Pg464CodeOnlyDeployment.class'"),
    )
    for old, new in replacements:
        assert raw.count(old) == 1, old
        raw = raw.replace(old, new)
    for old, new in (
        ('pg635-resume-tools-v1','pg647-retirement-tools-v1'),
        ('pg635-resume-stage-v1','pg647-retirement-stage-v1'),
        ('Pg635ResumePreparation','Pg647RuntimeRetirement'),
        ('pg635-compile-v1','pg647-compile-v1'),
        ("'pg635-'", "'pg647-'"), ('PG635_STAGED','PG647_STAGED'),
    ):
        assert old in raw; raw = raw.replace(old, new)
    assert 'Pg635ResumePreparation' not in raw and "('stage','prepare')" not in raw
    return raw


if __name__ == '__main__':
    exec(compile(source(), str(R/'pg647_retirement_native.py'), 'exec'),
         {'__name__':'__main__', '__file__':str(R/'pg647_retirement_native.py')})
