"""UI233 + SS323 approved literal rows versus the existing independent fixture; no product code."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=load(R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24534-protocol-limits-before-git-v1/manifest.json');main=before['approvedMain'];ui='documents/200_UI/230_インターフェース/233_固定長電文インターフェース一覧.md';ss='documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md'
def approved(p):
 b=subprocess.check_output(['git','show',main+':'+p]);assert hashlib.sha256(b).hexdigest()==before['approvedDesigns'][p]['sha256'];return b.decode()
rows=[]
for line in approved(ui).splitlines():
 c=[x.strip() for x in line.strip('|').split('|')]
 if len(c)!=9:continue
 m=re.fullmatch(r'([QSE]) `([A-Z0-9]{8})`',c[1])
 if not m:continue
 nums=[int(x.replace(',','')) for x in c[3:7]];assert nums[3]==256+nums[0]+nums[1]*nums[2] and nums[3]<=1000000;rows.append([m[2],m[1],c[2],*nums])
assert len(rows)==64 and len({r[0] for r in rows})==64 and sum(r[5]>0 for r in rows)==14 and sum(r[1]=='S' for r in rows)==31
ssRows={}
for line in approved(ss).splitlines():
 m=re.match(r'^\| `([A-Z0-9]{8})` ([\d,]+)/([\d,]+)/([\d,]+)/([\d,]+) \|',line)
 if m:assert m[1] not in ssRows;ssRows[m[1]]=[int(m[i].replace(',','')) for i in range(2,6)]
assert len(ssRows)==64 and all(ssRows[r[0]]==r[3:] for r in rows)
fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/layouts-ui233.tsv';assert sha(fixture)==before['unchangedGoldenResourceHashes'][str(fixture.relative_to(R))];actual=[]
for line in fixture.read_text().splitlines():
 if line.startswith('#'):continue
 c=line.split('\t');assert len(c)==7;actual.append([*c[:3],*map(int,c[3:])])
assert actual==rows
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24548-protocol-independent-limits64-v1';assert not out.exists();out.mkdir();(out/'approved-limits64.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',approvedMain=main,approvedDesigns={ui:before['approvedDesigns'][ui],ss:before['approvedDesigns'][ss]},existingFixture=dict(path=str(fixture.relative_to(R)),sha256=sha(fixture)),rows=64,repeatingRows=14,responseRows=31,headerBytes=256,allIndependentScalarEquations=True,ssScalarEquality=True,existingFixtureEquality=True,newDuplicateFixtureGenerated=False,productMethodInvoked=False,productTestsExecuted=0,oldGoldenFixtureHashes=before['unchangedGoldenResourceHashes'],newAcceptance=0,formalUpdated=False,effortRate=None,files={'approved-limits64.json':sha(out/'approved-limits64.json')},toolSha256=sha(Path(__file__)));(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,independent64=64,repeating14=14,response31=31,fixtureReused=True,manifestSha256=sha(out/'manifest.json'))))
