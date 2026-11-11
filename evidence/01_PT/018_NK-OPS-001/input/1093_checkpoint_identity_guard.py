"""Isolate the actual pure identity binder AST; no stage, event or product side effects."""
from pathlib import Path
import ast,hashlib,json,re,datetime as dt
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=B/'input/1069_wbs65_stage_record.py'
t=ast.parse(p.read_text());nodes=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='bind_current_identity'];assert len(nodes)==1
namespace={'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),namespace);bind=namespace['bind_current_identity']
head='f76ad51e73ad0a7c54a3c50ddc5e3cdb57f9aca4';main='7aed8eace7c844c2f79f2e39db766faf914890d5';old=dict(head='b713991f750eefe0982f94564480a378f06d3ff6',productionCoreMain='4217e14083c6ecac116216e08d57f4361eb2f12d',formalTests=1964,formalScopes=53,ordinaryActiveGroup='fixed',historicalBudget=269.8)
copy=json.loads(json.dumps(old));new=bind(old,head,main);assert old==copy and new['head']==head and new['productionCoreMain']==main
assert new['identityBindingHistory'][0]['previous']=={k:old[k] for k in ['head','productionCoreMain']} and all(new[k]==old[k] for k in ['formalTests','formalScopes','ordinaryActiveGroup','historicalBudget'])
assert bind(new,head,main)==new
checks=0
for a,b in [(True,main),(head,None),('0'*39,main),(head,'G'*40)]:
 try:bind(old,a,b)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid identity accepted')
S=R.parent/'PMO/pgpt-completion-stage-20261102';aliases={}
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 d=json.loads((S/name).read_text());n=bind(d,head,main);assert n['lastEventId']==d['lastEventId']
 (S/name).write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n');aliases[name]=dict(head=n['head'],productionCoreMain=n['productionCoreMain'],priorIdentityPreserved=True)
O=B/'evidence/PG26056-checkpoint-identity-guard-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),aliases=aliases,aliasCount=3,negativeMetadataChecks=checks,oldStateUnmodified=True,idempotentBinding=True,formalOrBudgetChanges=False,oldEventsRewritten=False,productTestsExecuted=0,newAcceptance=0,sourceToolSha256=hashlib.sha256(p.read_bytes()).hexdigest(),toolSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,aliasCount=3,negativeChecks=checks)))
