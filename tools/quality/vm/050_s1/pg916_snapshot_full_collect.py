"""Qualify fresh PG915 XML/static/source/byte/session; no old native/new-source mixing."""
from pathlib import Path
from pg858_completed_reference_collect import main as old_main
import inspect

R = Path(__file__).resolve().parent


def code():
    raw = inspect.getsource(old_main)
    substitutions = (
        ('pg857-completed-reference-six-host-v1', 'pg915-snapshot-six-host-v1'),
        ('pg854-completed-reference-selected-v4', 'pg911-snapshot-selected-v5'),
        ('pg830-manager-six-host-v1', 'pg857-completed-reference-six-host-v1'),
        ('85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede', 'fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6'),
        ("any(name.startswith('dev/codex/schubert/nk/batch/file/'+n)for n in ('MaintenanceRunFiles','MorningNewRunAdmission','MorningResumeAdmission'))", "name=='dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.class'"),
        ('tests==3541 and suites==522', 'tests==3550 and suites==523'),
        ('2a0d5aa392c85a1dc12a1cdb423978e8500895b8', 'e01612fcd7f2752df5ae0836b78538fd5e87f120'),
    )
    for left, right in substitutions:
        assert raw.count(left) == 1, left
        raw = raw.replace(left, right)
    return raw


if __name__ == '__main__':
    import pg858_completed_reference_collect as old
    env = dict(old.__dict__)
    exec(compile(code(), '<PG916 new candidate whole six>', 'exec'), env)
    env['main']()
