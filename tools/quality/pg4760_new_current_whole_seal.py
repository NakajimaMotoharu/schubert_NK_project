"""Current normal full11 same-day whole seal; genuine guard and raw-before-parse retained."""
import ast
import json
from pyflakes.api import check
import pg4586_current_independent_acceptance as previous
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as terminal
import pg4756_new_current_same_day_rows as rows
import pg4742_same_day_query_oracle as oracle

SLOT='pg4760-new-current-whole-seal-v1'


def replace_constant(raw,name,value):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one sealed '+name)
    return raw.replace(ast.get_source_segment(raw,nodes[0]),name+'='+repr(value),1)


def payload(observed,before_hash):
    raw=terminal.bind(previous.seal_payload(observed,before_hash))
    raw=raw.replace(previous.SEAL,SLOT).replace(previous.ROWS,rows.SLOT)
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    raw=raw.replace(ast.get_source_segment(raw,node),admission.project_source(),1)
    independent=oracle.source()+'\nimport base64,stat\nfrom pathlib import Path\n'+rows.key_source()
    independent+='\ndef qualify_whole(old,new,cutoff,done,upper):\n    try:\n        require(instant(cutoff)<=instant(done)<=instant(upper))\n        return qualify(old,new,'+repr(observed['run'])+',cutoff,upper)\n    finally:KEY[:]=b"\\0"*len(KEY)\n'
    independent+='\n_original_qualify=qualify\nqualify_current=_original_qualify\n'
    # Whole seal calls business.qualify(old,new,cutoff,done,upper).
    independent=independent.replace('return qualify(old,new,','return qualify_current(old,new,')+'qualify=qualify_whole\n'
    raw=replace_constant(raw,'ORACLE',independent)
    genuine=terminal.payload(observed);marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+terminal.TERM+"')"
    if genuine.count(marker)!=1:raise ValueError('exact genuine terminal proof boundary')
    raw=replace_constant(raw,'GUARD',genuine[:genuine.index(marker)])
    if check(raw,'<new normal same-day full11 whole seal>'):raise ValueError('complete outer namespace')
    if check(independent,'<full independent same-day SQL capsule>'):raise ValueError('complete SQL capsule')
    compile(raw,'<new current seal>','exec');return raw


def main():
    for slot in [terminal.TERM,rows.SLOT]:
        value=json.loads((admission.W/slot/'manifest.safe.json').read_bytes())
        if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==admission.SOURCE):raise ValueError('same genuine terminal and all24 first')
    return admission.execute(SLOT,payload(admission.live(),admission.before()),90)


if __name__=='__main__':raise SystemExit(main())
