"""SSC260 all-field reload projection: no arbitrary history ignore."""
import re
import ast
from pathlib import Path

_tree=ast.parse(Path(__file__).with_name('pg477_unit_references.py').read_bytes())
_nodes=[n for n in _tree.body if isinstance(n,ast.FunctionDef)and n.name=='exec_record']
if len(_nodes)!=1:raise ValueError('fixed pure exec parser refused')
exec(compile(ast.Module(body=_nodes,type_ignores=[]),'<pure fixed exec parser>','exec'),globals())

MORNING='schubert-nk-morning-controller.service'
WRONG='/run/systemd/system/schubert-nk-morning-controller.service.d/pg1160-once-resume.conf'
RESET=('n/a','n/a','0','(null)','0/0')


def configuration(old,current,wrong_loaded):
    if type(old)is not dict or type(current)is not dict or set(old)!=set(current)or type(wrong_loaded)is not bool:raise ValueError('fixed reload projection refused')
    for unit,before in old.items():
        after=current[unit]
        if type(before)is not dict or type(after)is not dict or set(before)!=set(after):raise ValueError('fixed reload fields refused')
        exclusions={'ExecStart','DropInPaths'}if unit==MORNING and wrong_loaded else {'ExecStart'}
        if any(before[k]!=after[k]for k in before.keys()-exclusions):raise ValueError('nondeclaration setting drift refused')
        a,b=exec_record(before['ExecStart']),exec_record(after['ExecStart'])
        if a is None or b is None or a[:3]!=b[:3]or b[3:]not in (a[3:],RESET):raise ValueError('reload declaration/history refused')
        if unit==MORNING and wrong_loaded:
            paths=before['DropInPaths'].split()+[WRONG]
            if len(paths)!=len(set(paths)):raise ValueError('duplicate wrong runtime refused')
            expected=' '.join(sorted(paths,key=lambda p:p.rsplit('/',1)[-1]))
            if after['DropInPaths']!=expected:raise ValueError('finite dropin order refused')
    return True
