"""Write concrete original criteria decisions without converting technical proof into acceptance."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def find(x,ids):
 out=[]
 if isinstance(x,dict):
  if x.get('id') in ids:out.append(x)
  for v in x.values():out.extend(find(v,ids))
 elif isinstance(x,list):
  for v in x:out.extend(find(v,ids))
 return out
p481=next((r/'documents/400_PGPT/470_PMO').glob('481_*.json'));p484=next((r/'documents/400_PGPT/470_PMO').glob('484_*.json'))
parent=find(load(p481),{'WBS-P020-01'})[0];foundation=find(load(p481),{'WBS-F02'})[0];children=find(load(p484),{'WBS-P020-01.01','WBS-P020-01.02','WBS-P020-01.03'})
assert len(children)==3 and foundation['acceptance']['status']!='ACCEPTED' and parent['acceptance']['status']!='ACCEPTED'
unit=b/'evidence/PG37020-p020-current-quality-join-v1/manifest.json';values=b/'evidence/PG37026-values5-session-closure-v1/manifest.json';assert load(unit)['success']==124 and load(values)['success']==5
shared=[ref(unit),ref(values)];decisions=[]
for child in sorted(children,key=lambda x:x['id']):
 for check in child['acceptanceChecks']:
  quality=check['id'].endswith(':quality')
  decisions.append(dict(id=check['id'],originalExpected=check['expected'],status='PARTIAL_UNRESOLVED_QUALITY' if quality else 'TOOLS_CONTRACT_PROVEN_REAL_CAPTURE_NOT_IMPLIED',evidence=shared,sourceCore=load(unit)['sourceCore'],actualWhole124Source=load(unit)['actualUnitSource'],actualNew5Source=load(values)['actualUnitSource'],scope='Same exact five Main/ten physical; source changes only new Test, separate execs',newAccepted=False,
   satisfied=['Same source and baseline immutability on isolated snapshot','Independent whole124 success and five new value contracts separately','Full five Main/ten physical lint/CS/SB and fifteen PMD site decisions'] if quality else [child['title']+' tool-only contract matched to literal Test and current public manifest'],
   missing=['Raw private utility constructor four methods and compiler cleanup/default branch conditions remain unclosed; original raw5L18M34B184I not replaced by union','Original F02 exit dependency not ACCEPTED; individual criteria cannot bypass dependency','Method/requirement/TestID trace joins and final same-source quality certification remain'] if quality else ['F02 dependency and quality criterion unresolved; real Current/NK/CHR original conditions separate']))
for check in parent['acceptanceChecks']:
 decisions.append(dict(id=check['id'],originalExpected=check['expected'],status='NOT_ACCEPTED',evidence=shared,reason='Three original children/end dependency not fully accepted; tool124 and independent5 do not establish actual native/CHR or full451',newAccepted=False))
out=b/'evidence/PG37030-p020-original-criteria-decision-v1';out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=load(unit)['sourceCore'],actualUnitSource=load(values)['actualUnitSource'],originalParent='WBS-P020-01',originalChildIds=sorted(x['id'] for x in children),criteria=decisions,originalFoundationDependency=foundation['id'],foundationStatus=foundation['acceptance']['status'],originalParentStatus=parent['acceptance']['status'],acceptance='NOT_ACCEPTED',newAcceptance=0,accepted190Baseline=17,netOriginalIncrease=0,historicalFormal=dict(tests=1964,scopes=53),effortCompletionRate=None,oldSuccessRequalifiedAsNewAcceptance=False,sourceDomain='Main unchanged / actual124 Unit1f5, new5 Unit6cc; no single combined129 run or exec union',scopePlanPins=[ref(p481),ref(p484)],action='Continue original F03 PMD source-matched applicability review. QA056 four product classfile phases and exact individual safety/actual-native/Root holds remain. Do not regenerate current124 or already qualified Main477/SB for confirmation.')
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(d/'056_P020三子個別判定・未成立条件.md').write_text('# P020 三子の個別条件返却\n\nPG37030の元criteria全件とF02依存を照合。共通五Main/10physical/whole124の工具契約とstatic、同一Mainの別新五件を証明したが、三子のquality・親の終了依存は未成立。新規受入0、17/190不変、1964/53不変、工数null。未成立をNOT_ACCEPTEDとして明記し、小試験成功を実CHR/NK/全451へ換算しない。\n\n次の取得証拠はF03の原PMD971中未分類662について、まずstandalone/J2EEの適用条件を各site/主owner/元SS・Java25構成へ対応させる。解析済みraw/sourceは不変のため試験/全SB/全回帰を確認再演しない。QA056の四型範囲の承認前にclassfile操作せず、他独立作業を継続する。\n')
print(json.dumps(dict(actualExit=0,criteria=len(decisions),children=3,foundation=foundation['acceptance']['status'],newAcceptance=0,netIncrease=0)))
