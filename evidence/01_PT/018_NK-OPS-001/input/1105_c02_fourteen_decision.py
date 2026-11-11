"""Fourteen configuration source/independent literal and scope-bound original receipt audit."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26076-c02-fourteen-decision-v1'
P=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
rows=list(csv.DictReader((P/'C02の14設定と該当証拠の区分.tsv').open(encoding='utf-8-sig'),delimiter='\t'));assert len(rows)==14
w=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');owner=next(x for x in w['tasks'] if x['id']=='WBS-C02');assert {x['管理対象'] for x in rows}==set(owner['ownedArtifacts'])
proofpairs=[('PG16890-public-unit-files-original-fourteen-pt-v1','fc790c6a89f4ff1148f8f320a2908b27c14c5540b1d195a846dddba6e2b7b52f'),('PG16893-public-unit-files-original-fourteen-post-v2','47876c06dd3d76cfbd4a759e6da4eb1470c959d83facdde342aead8eba968a34'),('PG16894-public-unit-files-original-fourteen-independent-v1','274360f7060afaad6ed68c791f01d7c2823304b9da4badc6d96fa3a4cd724545'),('PG16714-supplementary-unit-template-original-five-post-v1','da1df35232073867a24c00569710cb3644fc45c9ea5b0035bd465d42cbc6b67b'),('PG17500-inspector-deployment-eight-pt-v1','7fec86110b87d453a89b3ec57348754664d40248567d2ec6dc5eb7ef40336c57'),('PG17504-inspector-deployment-eight-post-v2','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f')]
proofs={};references=[]
for n,h in proofpairs:
 p=E/'provisional'/n/'manifest.json';assert sha(p)==h;d=load(p);assert type(d['actualExit']) is int and d['actualExit']==0;proofs[n]=d;references.append(dict(path=str(p.relative_to(R)),sha256=h,source=d['source']))
raw=proofs[proofpairs[0][0]];post=proofs[proofpairs[1][0]];supp=proofs[proofpairs[3][0]];inspector=proofs[proofpairs[4][0]];assert raw['tests']==14 and inspector['tests']==8
# Preserve duplicate/list directives, including empty reset lines; no manager/parser execution.
def directives(path):
 out={};section=None
 for line in path.read_text().splitlines():
  if not line.strip() or line.lstrip().startswith('#'):continue
  if line.startswith('[') and line.endswith(']'):section=line[1:-1];continue
  assert section is not None and '=' in line
  k,v=line.split('=',1);out.setdefault(section+'.'+k,[]).append(v)
 return out
expected={
'artemis.service':{'Type':'simple','User':'schubert-artemis','Group':'schubert-artemis','Restart':'on-failure','SuccessExitStatus':'143','TimeoutStartSec':'120s','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-api.service.template':{'Type':'simple','User':'schubert-api','Group':'schubert-api','Restart':'on-failure','TimeoutStartSec':'120s','TimeoutStopSec':'60s','SendSIGKILL':'no','UMask':'0027'},
'schubert-nk-web.service.template':{'Type':'simple','User':'schubert-web','Group':'schubert-web','Restart':'on-failure','TimeoutStartSec':'120s','TimeoutStopSec':'30s','SendSIGKILL':'no','UMask':'0027'},
'schubert-nk-backup.service.template':{'Type':'oneshot','User':'schubert-backup','Group':'schubert-backup','Restart':'no','RemainAfterExit':'yes','TimeoutStartSec':'30min','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-bootstrap-admin.service.template':{'Type':'oneshot','User':'schubert-api','Group':'schubert-api','Restart':'no','SuccessExitStatus':'20','TimeoutStartSec':'30s','TimeoutStopSec':'30s','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-cleanup.service.template':{'Type':'oneshot','User':'root','Group':'root','Restart':'no','RemainAfterExit':'yes','SuccessExitStatus':'10','TimeoutStartSec':'30min','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-expiry-cleanup.service.template':{'Type':'oneshot','User':'root','Group':'root','Restart':'no','RemainAfterExit':'yes','SuccessExitStatus':'10','TimeoutStartSec':'10min','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-inbox-inspector.service':{'Type':'oneshot','User':'schubert-inbox-inspector','Group':'schubert-inbox-inspector','Restart':'no','RemainAfterExit':'yes','SuccessExitStatus':'10','TimeoutStartSec':'30min','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-morning-controller.service.template':{'Type':'oneshot','User':'root','Group':'root','Restart':'no','SuccessExitStatus':'10','TimeoutStartSec':'30min','TimeoutStopSec':'60s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0077'},
'schubert-nk-startup-policy.conf':{'Type':'notify','User':'caddy','Group':'caddy','Restart':'no','TimeoutStartSec':'30s','TimeoutStopSec':'30s','KillMode':'control-group','SendSIGKILL':'no','UMask':'0027'},
'schubert-nk-stop-policy.conf':{'TimeoutStopSec':'30s','SendSIGKILL':'no'}}
checks=[]
for row in rows:
 name=row['管理対象'];p=R/name;assert subprocess.check_output(['git','hash-object',name],text=True).strip()==row['候補sourceのblob'];assert sha(p)==raw['begin']['sourceHashes'][name]
 d=directives(p);fixed=expected.get(p.name,{})
 for k,v in fixed.items():assert d['Service.'+k]==[v],(name,k)
 if p.name in expected and p.name not in ['schubert-nk-stop-policy.conf','schubert-nk-startup-policy.conf']:
  assert d['Service.NoNewPrivileges']==['true'] and d['Service.ProtectSystem']==['strict'] and d['Service.ProtectHome']==['true']
  assert d['Service.RestrictAddressFamilies']==['AF_UNIX AF_INET AF_INET6']
 if '/optional/' in name:
  id='api-context-aes-previous' if 'context-previous' in name else 'api-inbox-response-aes-previous';assert d=={'Service.LoadCredential':[id+':/etc/schubert-nk/credentials/'+id]}
 if p.name=='schubert-nk-morning.target.template':assert d['Unit.Requires']==d['Unit.After']==['schubert-nk-morning-controller.service'] and not any(k.endswith('.Wants') for k in d)
 if name in post['publicResourceInputs']:reference='PG16890 original14/seven configuration files, Main credit0'
 elif name in supp['publicResourceInputs']:reference='PG16714 original5/four configuration files, Main credit0'
 else:reference='PG17500/17504 inspector original8/three Unit-profile files, current changedTest not yet rerun'
 checks.append(dict(path=name,sha256=sha(p),gitBlob=row['候補sourceのblob'],declaredDirectives=d,fixedDesignExpectations=fixed,reference=reference,sourceLiteralsCorrespond=True,effectiveManagerSettingsVerified=False,currentTestReexecution=False,remaining=['Fresh effective merged Unit/default/NSS/dependency/timeout ownership and real release/credential/path conditions not proven by file literals.','Current source 451/native/parent endings remain separate HOLD.']))
xml=[]
for filename,h in raw['xmlHashes'].items():
 p=E/'provisional'/proofpairs[0][0]/filename;assert sha(p)==h;root=ET.parse(p).getroot();assert all(root.get(k)=='0' for k in ['failures','errors','skipped']);xml+= [(c.get('classname'),c.get('name')) for c in root.findall('testcase')];assert all(not list(c) for c in root.findall('testcase'))
assert len(xml)==len(set(xml))==14
for name,h in raw['begin']['testSourceHashes'].items():
 if '/src/test/' in name:assert sha(Path(name))==h
ip=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDeploymentTest.java';before=E/'PG26078-inspector-profile-oracle-before-v1/before1.java';text=ip.read_text();old=before.read_text();assert text.replace('                  "maintenance-owner",\n','').replace('assertEquals(4 + selection.size(), ids.size());','assertEquals(3 + selection.size(), ids.size());')==old
assert hashlib.sha256(old.encode()).hexdigest()==inspector['begin']['testSourceHashes'][str(ip)]
assert text.count('@Test')==8
for number in ['342','343']:
 paths=list((R/'documents/300_SS/340_batch・基盤').glob(number+'_*.md'));assert len(paths)==1;assert paths[0].read_bytes()==subprocess.check_output(['git','show','origin/main:'+str(paths[0].relative_to(R))])
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',wbs='WBS-C02',configurationCount=14,checks=checks,referenceProofs=references,originalPublic14Cases=xml,inspectorOriginalTestsReferenced=8,currentInspectorTestSha256=sha(ip),inspectorOracleFix=dict(bug='BUG-2631',ykt='YKT-2312',baseCount=4,profiles=[4,5,5,6],onlyTwoLiteralChanges=True,afterFixTestStatus='NOT_RUN_NOT_PASS'),inspectorOwnedCleanupGap=dict(bug='BUG-2632',ykt='YKT-2313',status='OPEN_SOURCE_CONFIRMED_PT_PENDING'),criteria=dict(reuse='EXACT_PUBLIC_RESOURCE_BYTE_REFERENCE_ONLY',contract='STATIC_DECLARATIONS_CORRESPOND_DYNAMIC_ENDINGS_MISSING',scope='FOURTEEN_CONFIGURATIONS_MATCH_OWNER_AND_PLAN',quality='NOT_ACCEPTED_CURRENT_TEST_FIX_NOT_RUN_EFFECTIVE_RUNTIME_AND_451_PENDING'),decision='NOT_ACCEPTED',newAcceptance=0,formalUpdated=False,productTestsExecuted=0,newCoverageMeasurements=0,actualUnitServiceVmDbOperations=0,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,configs=14,decision='NOT_ACCEPTED',productTestsExecuted=0,sha256=sha(O/'manifest.json'))))
