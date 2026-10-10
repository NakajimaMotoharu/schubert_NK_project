"""Read-only canonical runtime verification within fresh complete owned scopes."""
import ast
from pg1172_runtime_sources import files as previous
from pg1134_failed_recovery_sources import replace

BASE = '/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/canonical-runtime-owner-handoff-v1/after.private.json'
HASH = 'd218c5e294937078d6535b1871552a2bac1f4a3a81c8a46f47f0f018b79b8550'


def files():
    values = previous()
    result = {}
    for name, text in values.items():
        name = name.replace('Pg1172RuntimeResume', 'Pg1179RuntimeVerify').replace('pg1172_runtime', 'pg1179_runtime')
        text = text.replace('Pg1172RuntimeResume', 'Pg1179RuntimeVerify').replace('PG1172', 'PG1179').replace('pg1172_runtime', 'pg1179_runtime').replace('pg1172-runtime-tools-v1', 'pg1179-runtime-tools-v1').replace('pg1172-runtime-resume-v1', 'pg1179-runtime-verify-v1')
        if name.endswith('_refs.py'):
            text = text.replace('wrong-runtime-post-v1/after.private.json', 'canonical-runtime-owner-handoff-v1/after.private.json').replace('a936fd3e8f851255acc66156a99db967b52195033dea4b75cf2515e3bce7b36c', HASH)
            start = text.index('def require_runtime_configuration(')
            end = text.index('def execute():', start)
            text = text[:start] + CONTRACT + text[end:]
            text = replace(text, 'and not list(RUNTIME.iterdir())', 'and {p.name for p in RUNTIME.iterdir()}=={runtime.NAME}')
            text = replace(text, "['before','terminal','prepare','prepared','release']", "['before','terminal','verify','prepared','release']")
            start = text.index("   if action=='prepare':")
            end = text.index("   if action=='prepared':", start)
            text = text[:start] + "   if action=='verify':\n    require_runtime_configuration(runtime_configuration());require_runtime_tree();changed=True\n" + text[end:]
            text = text.replace('[404585,404614,253968]', '[404585,404614,253968,420139,420168]')
            ast.parse(text)
        elif name.endswith('.java'):
            text = replace(text, 'phase="FIXED_RUNTIME_PREPARATION";refs.check("prepare")', 'phase="CANONICAL_RUNTIME_VERIFICATION";refs.check("verify")')
        result[name] = text
    return result


CONTRACT = r'''
def require_runtime_configuration(actual):
 require(actual==baseline['configuration'])
 morning=actual[MORNING];record=exec_record(morning['ExecStart'])
 require(record is not None and record[1].endswith(' --resume '+runtime.RUN_ID))
 require(morning['DropInPaths'].split()[-1]==str(RUNTIME/runtime.NAME))
def runtime_tree():return tree(pathlib.Path('/run/systemd/system'))
def require_runtime_tree():
 value=runtime_tree();require(value==baseline['runtime'])
 target=RUNTIME/runtime.NAME
 require({p.name for p in RUNTIME.iterdir()}=={runtime.NAME})
 require(value[str(target)]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)]and target.read_bytes()==dropin)
 require(value[str(target)]['sha256']==hashlib.sha256(dropin).hexdigest())
 require(command(['/usr/bin/findmnt','--target',str(RUNTIME),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
'''
