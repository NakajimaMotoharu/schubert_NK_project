"""BUG1385 new host once after known pre-reservation refusal; existing staged tools retained."""
import ast
import inspect
import json
from collections import Counter
import pg4776_new_current_owned_dispatch as previous
import pg2556_strict_current_owned_dispatch as constructor_source
from immutable_payload_binding import PROTECTED
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


def rename_output(raw,expected,slot):
    original=capsules(raw);result=previous.rename_output(raw,expected,slot)
    nodes=[n for n in ast.parse(result).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='RAW_SAVE'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one explicit raw evidence output role')
    n=nodes[0];v=n.value
    if not(isinstance(v,ast.BinOp)and isinstance(v.op,ast.Div)and isinstance(v.left,ast.Name)and v.left.id=='BASE'and isinstance(v.right,ast.Constant)and v.right.value==expected+'-raw'):raise ValueError('exact original raw output slot')
    old=ast.get_source_segment(result,n)
    result=result.replace(old,'RAW_SAVE=BASE/'+repr(slot+'-raw'),1)
    if capsules(result)!=original:raise ValueError('all protected snapshots and oracles unchanged')
    return result


def run_source():
    raw=previous.namespace()['run_source']()
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='rename_output')
    # The transport runtime receives this host helper, not its emitted definition.
    raw=raw.replace(ast.get_source_segment(raw,node),'',1)
    replacements=[("base = W / ('pg4776-' + action + '-v1')","base = W / ('pg4806-' + action + '-v1')"),
      ('pg4777-parent-two-source-prequalification-v1','pg4807-parent-two-source-prequalification-v1'),
      ('pg4779-newboot-pre-stop-full-v1','pg4809-newboot-pre-stop-full-v1')]
    for old,new in replacements:
        if old not in raw:raise ValueError('one new continuation boundary '+old)
        raw=raw.replace(old,new)
    raw=raw.replace("if action not in ('stage', 'stop'):","if action != 'stop':",1)
    return raw


def runtime():
    ns=previous.namespace()
    constructor=ns['run_action']
    raw=previous.role.bind(inspect.getsource(constructor_source.run_action));env={**constructor.__globals__}
    exec(compile(raw,'<original constructor only definition>','exec'),env)
    if env['run_action'].__code__.co_code!=constructor.__code__.co_code or env['run_action'].__code__.co_consts!=constructor.__code__.co_consts:raise ValueError('exact existing actual runtime constructor')
    tree=ast.parse(raw);fn=tree.body[0]
    if len(fn.body)!=4:raise ValueError('two namespace assignments then exec/entry')
    fn.body=fn.body[:2]+[ast.Return(value=ast.Name(id='ns',ctx=ast.Load()))]
    ast.fix_missing_locations(tree);exec(compile(tree,'<pure original runtime constructor>','exec'),env)
    values=env['run_action']('NO_OPERATION')
    values['PARENT_PREQUAL']="import os\nif os.path.lexists('/var/lib/pgpt-s1-preservation/pg4772-native-stop-v1'):raise ValueError('existing guest stop; recover, never replay')\n"+values['PARENT_PREQUAL']
    values['rename_output']=rename_output
    script=run_source();exec(compile(script,'<new-only normal continuation runtime>','exec'),values)
    return values


def main():
    import sys
    if sys.argv[1:]!=['stop']:raise ValueError('only explicitly authenticated new continuation')
    previous.authenticate_host();w=previous.role.admission.W
    proof=json.loads((w/'pg4779-newboot-pre-stop-full-v1.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==1 and proof['payloadSha256']=='a1c1bd2bb33b5a5b64ea5ee3cb11c7ebcad646075e2ea36fafcb218da9b46f05'):raise ValueError('exact known pre-reservation refusal')
    if any((w/('pg4776-stop-v1'+suffix)).exists()for suffix in ['.private.log','.exit','.safe.json']):raise ValueError('original operation may have issued; recover first')
    with management_gate(P/'current-management-critical.lock'):return runtime()['run_action']('stop')


if __name__=='__main__':raise SystemExit(main())
