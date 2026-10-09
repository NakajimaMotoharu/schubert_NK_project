"""Independent new source full XML/byte/session/static qualifier; old native not imported."""
import inspect
from pg858_completed_reference_collect import main as previous
def code():
    raw=inspect.getsource(previous)
    values=(
      ('pg857-completed-reference-six-host-v1','pg926-body-six-host-v1'),
      ('pg854-completed-reference-selected-v4','pg925-body-selected-v2'),
      ('pg830-manager-six-host-v1','pg915-snapshot-six-host-v1'),
      ('85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede','abd7d3f09463ae3dc025f4ed33154f107697afd39966451693c32b5c2383c416'),
      ("classes((selected/'batch' if module=='batch' else old/module)/jar)", "classes((selected/module if module in ('bootstrap','api') else old/module)/jar)"),
      ("module=='batch' and any(name.startswith('dev/codex/schubert/nk/batch/file/'+n)for n in ('MaintenanceRunFiles','MorningNewRunAdmission','MorningResumeAdmission'))", "(module=='bootstrap' and name in ('dev/codex/schubert/nk/bootstrap/ChildStartupContext.class','dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo.class')) or (module=='api' and name=='dev/codex/schubert/nk/api/file/InspectorApplication.class')"),
      ('tests==3541 and suites==522','tests==3560 and suites==523'),
      ('2a0d5aa392c85a1dc12a1cdb423978e8500895b8','e01612fcd7f2752df5ae0836b78538fd5e87f120'),
    )
    for before,after in values:
        assert raw.count(before)==1,before;raw=raw.replace(before,after)
    return raw
if __name__=='__main__':
    import pg858_completed_reference_collect as old
    env=dict(old.__dict__);exec(compile(code(),'<PG927 new body source qualifier>','exec'),env);env['main']()
