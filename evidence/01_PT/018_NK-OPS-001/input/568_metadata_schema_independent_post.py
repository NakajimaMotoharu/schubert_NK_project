"""Independent inverse-byte/field/schema witnesses and future completion-setter guards."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG23894-ledger6-package3-schema-correct-v1';O=B/'evidence/PG23896-ledger6-package3-schema-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='8e2ad5f30f2caaa6679bd07ef8cf4ef3dccc9698cd9714f20b861bd9876150fe'
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(P/n)==h
lp=R/m['ledgerAfter']['path'];wp=R/m['wbsAfter']['path'];assert sha(lp)==m['ledgerAfter']['sha256'] and sha(wp)==m['wbsAfter']['sha256']
changes=load(P/'ledger-row-changes.json');text=lp.read_text();restored=text
assert len(changes)==6 and {v['id'] for v in changes}==set(cfg['dateRowsBefore'])
for v in changes:
 before=v['before'];after=v['after'];assert before==cfg['dateRowsBefore'][v['id']] and text.splitlines().count(after)==1
 a=[x.strip() for x in before.split('|')[1:-1]];z=[x.strip() for x in after.split('|')[1:-1]]
 assert len(a)==15 and len(z)==16 and a[:-1]==z[:-2]
 assert a[-1]=='CLOSED  2026-11-08' and z[-2:]==['CLOSED','2026-11-08']
 assert after==before.replace('CLOSED  2026-11-08','CLOSED | 2026-11-08')
 restored=restored.replace(after,before,1)
assert hashlib.sha256(restored.encode()).hexdigest()==cfg['ledgerBefore']['sha256']
own=[line for line in text.splitlines() if re.match(r'\| BUG-(?:2499|250[0-9]) \|',line)];assert len(own)==11 and all(len(v.split('|')[1:-1])==16 for v in own)
wb=load(wp);kind=load(P/'package-kind-changes.json');assert len(kind)==3
rows={v['path']:v for v in wb['artifacts']};old=copy.deepcopy(wb);oldRows={v['path']:v for v in old['artifacts']}
for change in kind:
 n=change['path'];before=change['before'];after=change['after'];assert before in cfg['kindRowsBefore'] and rows[n]==after
 assert before['kind']=='JAVA' and after['kind']=='JAVA_PACKAGE'
 assert {k:v for k,v in before.items() if k!='kind'}=={k:v for k,v in after.items() if k!='kind'}
 oldRows[n]['kind']='JAVA'
assert hashlib.sha256((json.dumps(old,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()==cfg['wbsBefore']['sha256']
indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
packages=[v for v in wb['artifacts'] if v['path'].endswith('/package-info.java')];assert len(packages)==37
def package_valid(row):
 physical=[v for v in index.values() if v['path']==row['path']]
 return row['kind']=='JAVA_PACKAGE' and bool(physical) and all(v['hasCode'] is False for v in physical)
assert all(package_valid(v) for v in packages)
for row in packages:
 bad=copy.deepcopy(row);bad['kind']='JAVA';assert not package_valid(bad)
spec=importlib.util.spec_from_file_location('own_ledger_completion_guard',R/m['tool']['path']);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
valid=changes[0]['after'];assert mod.complete_row(valid,'2026-11-08')==valid
negatives=[]
for label,row,date in [('fifteen-columns',changes[0]['before'],'2026-11-08'),('seventeen-columns',valid+' |','2026-11-08'),('line-break',valid+'\n','2026-11-08'),('missing-pipes',valid.strip('|'),'2026-11-08'),('invalid-calendar',valid,'2026-02-30'),('unknown-date',valid,None),('non-canonical-date',valid,'2026-1-8')]:
 try:mod.complete_row(row,date)
 except ValueError:negatives.append(label)
 else:raise AssertionError('invalid future ledger update was accepted')
assert m['sourceMutation'] is False and m['productTestsExecuted']==m['newAcceptance']==0
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),ledgerAfter=m['ledgerAfter'],wbsAfter=m['wbsAfter'],fixedDateRows=6,fixedKindRows=3,currentTurnLedgerRowsValidated=11,expectedColumns=16,ledgerInverseExactByteHash=True,wbsInverseExactByteHash=True,allPackageMetadataRows=37,allPackageMetadataNoCode=True,packageMisclassificationNegatives=37,futureCompletionGuardNegatives=len(negatives),negativeLabels=negatives,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,bugs=['BUG-2508','BUG-2509'],ykts=['YKT-2246','YKT-2247'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,dates=6,kinds=3,packageRows37NoCode=True,futureLedgerNegatives=7,packageKindNegatives=37,inverseBytes=True,manifestSha256=sha(O/'manifest.json'))))
