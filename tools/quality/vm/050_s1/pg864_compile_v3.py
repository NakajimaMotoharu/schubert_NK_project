"""BUG982: dynamic Java SAVE expression and all explicit helper slots share v3."""
import ast
from pathlib import Path
import pg864_compile_v2 as old
R=Path(__file__).resolve().parent
def profile_v3(raw):
    for stem in ('pg864-completed-tools','pg864-prepare-ro','pg864-verify','pg864-activate'):raw=raw.replace(stem+'-v1',stem+'-v3')
    return raw.replace('"pg864-"+mode+"-v1"','"pg864-"+mode+"-v3"')
def source():
    raw=old.source().replace('pg864-completed-tools-v2','pg864-completed-tools-v3').replace('PG864-compile-v2','PG864-compile-v3').replace("'-v2.private.log'","'-v3.private.log'").replace('pg864-frozen-v2','pg864-frozen-v3').replace('profile_v2(value)','profile_v3(value)')
    ast.parse(raw);return raw
def profile_test():
    import re
    from pg864_completed_sources import sources
    actual={name:profile_v3(value)for name,value in sources().items()}
    java=actual['Pg864CompletedDeployment.java'];python=ast.parse(actual['pg864_completed_refs.py'])
    expr=re.search(r'save=BASE.resolve\("([^\"]+)"\+mode\+"([^\"]+)"\)',java);assert expr and expr.groups()==('pg864-','-v3')
    comparisons=[n for n in ast.walk(python)if isinstance(n,ast.Compare)and isinstance(n.left,ast.Call)and isinstance(n.left.func,ast.Name)and n.left.func.id=='str'and len(n.left.args)==1 and isinstance(n.left.args[0],ast.Name)and n.left.args[0].id=='SAVE']
    allowed=ast.literal_eval(comparisons[0].comparators[0]);expected=tuple('/var/lib/pgpt-s1-preservation/pg864-'+mode+'-v3'for mode in ('prepare-ro','verify','activate'));assert allowed==expected
    assert tuple('/var/lib/pgpt-s1-preservation/'+expr[1]+mode+expr[2]for mode in ('prepare-ro','verify','activate'))==expected
    assert '/var/lib/pgpt-s1-preservation/pg864-completed-tools-v3' in java
    for value in actual.values():assert 'pg864-prepare-ro-v1'not in value and '"pg864-"+mode+"-v1"'not in value
    assert 'pg861-runtime841-retired-post-v1/after.private.json'in actual['pg864_completed_refs.py']
    print('DEP864006 actual Java dynamic SAVE vs Python literal three modes + original861 preserved PASS')
if __name__=='__main__':
    profile_test()
    exec(compile(source(),'<864 dynamic and static profile closed v3>','exec'),{'__file__':str(R/'pg864_compile_v3.py'),'__name__':'__main__','regenerated':old.regenerated,'profile_v3':profile_v3})
