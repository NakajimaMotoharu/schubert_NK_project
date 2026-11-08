"""Independent document suffix/reference/numeric validation; no Product execution."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as E,datetime,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG24622-latest-handoff-update-v1';O=B/'evidence/PG24624-latest-handoff-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mp=S/'manifest.json';assert sha(mp)=='b0853a2cebd9802803452f2e96a4cb38fcd367c1ab53e9da582c888e4dfd5516';m=load(mp);block=(S/'latest-block.md').read_bytes();assert hashlib.sha256(block).hexdigest()==m['blockSha256']
refs=m['proofPins'];assert len(refs)==5
for n,h in refs.items():assert sha(R/n)==h
new=load(R/next(n for n in refs if '/PG24546-' in n));whole=load(R/next(n for n in refs if '/PG24584-' in n));denom=load(R/next(n for n in refs if '/PG24594-' in n));aliases=load(R/next(n for n in refs if '/PG24614-' in n));vendor=load(R/next(n for n in refs if '/PG24604-' in n))
xml=R/next(n for n in refs if '/PG24584-' in n);cp=xml.parent/'coverage.xml';assert sha(cp)==whole['files']['coverage.xml'];root=E.parse(cp).getroot();cs={x.get('type'):(int(x.get('covered')),int(x.get('missed'))) for x in root.findall('counter')};assert cs['LINE']==(3478,0) and cs['METHOD']==(742,0) and cs['CLASS']==(159,0) and cs['BRANCH']==(1014,0)
assert len(root.findall('.//class'))==169 and sum(bool(x.findall('method')) for x in root.findall('.//class'))==159 and denom['counts']==dict(inputBytes=176,xmlEntries=169,measuredClasses=159,annotations=7,abstractInterfaces=6,compilerSwitchMaps=4)
casepath=xml.parent/'testcases.safe.xml';assert sha(casepath)==whole['files']['testcases.safe.xml'];tree=E.parse(casepath).getroot();assert len(tree.findall('testcase'))==119 and not any(tree.findall('.//'+s) for s in ['failure','error','skipped']);assert whole['source']=='fa7ca8df24fbb4acea1b12b32f8f86aa07438b80' and new['source']=='8a027340a317584d5c80fb071e92da368439d07f'
assert new['newUniqueTests']==1 and new['tests']==16 and new['requalifiedExistingTests']==15 and vendor['newFalsePositives']==16 and aliases['newFalsePositives']==17 and aliases['cumulativeClassified']==1213 and aliases['remainingUnclassified']==3280 and aliases['actualSecretCount'] is None
unique=load(R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106/434_64layout独立上限・匿名Log16結果.json')['technicalMeasurementDelta'];assert unique['allUniqueAfter']==519 and unique['javaUniqueAfter']==415 and 415+97+7==519
text=block.decode();required=['PG/PT継続中・工程未完了','PT-WEB-20260925-24／1964PT／53scope','歴史WBS17/190','今回新規受入0件','工数完成率は未較正null','累計519＝Java415＋HTML97＋CSS7','24fixture119件一回OS0/FESaborted0','line3478/method742/class159/branch1014','分類1213／未分類3280','actualSecretCount=null','QA-055','回答「現行の固定文を維持する」','HTTP Retry-After','QA051 final','PG/PT残件をIT/STへ転嫁せず','旧PID/permit/旧runを再使用・そのまま復元せず','外部job/VMの現在状態は未認証','fresh残10%以下/取得不能']
assert all(s in text for s in required) and new['source'] in text and whole['source'] in text and whole['productionCoreMain'] in text
subprocess.run(['git','merge-base','--is-ancestor','42450b5','origin/main'],check=True)
expected={'documents/400_PGPT/401_PGPT成果物一覧.md',*[str(p) for p in Path('documents/400_PGPT/460_完了報告').glob('46[1234]_*.md')]};assert {x['path'] for x in m['documents']}==expected and len(expected)==5
checks=0;outrows=[]
def valid(raw,original):
 first,rest=original.split(b'\n',1);return raw==first+b'\n\n'+block+b'\n'+rest
for row in m['documents']:
 p=R/row['path'];raw=p.read_bytes();old=subprocess.check_output(['git','show',m['observerSource']+':'+row['path']]);assert hashlib.sha256(old).hexdigest()==row['beforeSha256'] and sha(p)==row['afterSha256'] and valid(raw,old);assert hashlib.sha256(old.split(b'\n',1)[1]).hexdigest()==row['historicalTailSha256']
 assert raw.count(b'<!-- PGPT-CURRENT-20261108-HANDOFF-BEGIN -->')==raw.count(b'<!-- PGPT-CURRENT-20261108-HANDOFF-END -->')==1
 for bad in [raw+b'x',raw.replace(b'119',b'120',1),raw.replace(b'PGPT-CURRENT-20261108-HANDOFF-END',b'BROKEN',1),b'X'+raw]:assert bad!=raw and not valid(bad,old);checks+=1
 outrows.append(dict(path=row['path'],sha256=sha(p),historicalTailExact=True))
def contract(v):
 assert type(v['actualExit']) is int and v['actualExit']==0 and type(v['documentsUpdated']) is int and v['documentsUpdated']==5 and v['historicalBytesPreserved'] is True and v['formalUpdated'] is False and v['pgptAllComplete'] is False and v['itStAccepted'] is False and v['allHoldsPreserved'] is True and v['effortRate'] is None and type(v['newAcceptance']) is int and v['newAcceptance']==0
contract(m)
for k,v in [('actualExit',False),('documentsUpdated',4),('formalUpdated',True),('pgptAllComplete',True),('itStAccepted',True),('allHoldsPreserved',False),('effortRate',1),('newAcceptance',False)]:
 bad=copy.deepcopy(m);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(m,sort_keys=True)
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false document completion')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=m['observerSource'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),proofPins=refs,documents=outrows,documentsUpdated=5,historicalBytesPreserved=True,metadataNegativeChecks=checks,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,pgptAllComplete=False,itStAccepted=False,allHoldsPreserved=True,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,documents=5,metadataNegatives=checks,manifestSha256=sha(O/'manifest.json'))))
