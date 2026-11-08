"""Reconcile current independent fixture cardinalities; no Product method or Java invocation."""
from pathlib import Path
from collections import defaultdict
import datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24744-current-component296-correction-v1';assert not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
before=load(B/'evidence/PG24742-component-count-documentation-before-v1/manifest.json')
for r in before['before']:assert sha(R/r['path'])==r['sha256']
normal=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG24642-protocol-whole120-independent-v1/manifest.json';assert sha(normal)=='8ebe6365bc701ba6432b1b55275004024dc71bc452d31b66d31c53894e3ae128'
n=load(normal);assert n['actualExit']==0 and n['tests']==120 and n['source']=='64f3a72753434347889f0eabd5d9f9dca67c6bfb'
parent=normal.parent;assert sha(parent/'testcases.safe.xml')==n['files']['testcases.safe.xml'];cases={c.get('classname')+'#'+c.get('name') for c in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')};key='dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allNamedTypesHaveIndependentDirectionalFieldMeaning()';assert key in cases
D=R/'src/schubert-nk-protocol/src/test/resources/protocol'
def fixture(name,width):
 p=D/name;assert hashlib.sha256(subprocess.check_output(['git','show',n['source']+':'+str(p.relative_to(R))])).hexdigest()==sha(p)
 rows=[l.split('\t') for l in p.read_text().splitlines() if l.strip() and not l.startswith('#')];assert rows and all(len(r)==width for r in rows);return rows
types=fixture('named-types-ss323.tsv',3);fields=fixture('fields-ui234-236.tsv',8);accessors=fixture('named-accessors-independent.tsv',2);assert len(types)==64 and len(fields)==389
getters=dict(accessors);assert len(getters)==len(accessors)==135
areas=defaultdict(list)
for row in fields:
 if row[6]!='F':areas[(row[0],row[1])].append(dict(name=row[2],length=int(row[4]),wire=row[5],presence=row[6],getter=getters[row[2]]))
shapes={};layouts=defaultdict(list)
for layout,data,record in types:
 for area,name in [('DATA',data),('RECORD',record)]:
  if name=='-':continue
  shape=areas[(layout,area)]
  if name in shapes:assert shapes[name]==shape
  else:shapes[name]=shape
  layouts[name].append(dict(layout=layout,area=area))
component=sum(map(len,shapes.values()));optional=sum(f['wire']=='X' and f['presence'] in ('C','O') for s in shapes.values() for f in s);empty=sum(not s for s in shapes.values())
assert len(shapes)==69 and component==296 and optional==79 and empty==4 and {f['name'] for s in shapes.values() for f in s}==set(getters)
helper=R/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle.java';assert hashlib.sha256(subprocess.check_output(['git','show',n['source']+':'+str(helper.relative_to(R))])).hexdigest()==sha(helper);text=helper.read_text();assert all(s in text for s in ['assertEquals(69, reviewed.size()', 'assertEquals(296, components,', 'assertEquals(79, optionals,', 'assertEquals(4, emptyTypes,'])
# Do not mutate the old producer/config/frozen specification; correction is mandatory supplemental evidence.
frozen=[r for r in before['before'] if '/input/' in r['path'] or '/evidence/' in r['path'] or Path(r['path']).name.startswith('3901_')]
active=[]
for r in before['before']:
 p=R/r['path']
 if p.name.startswith(('1197_','3902_')):
  original=p.read_text();assert original.count('295')==r['old295Occurrences'];corrected=original.replace('295','296');corrected+='\nBUG2552/YKT2276補足：現component期待数は296。旧295を含む1197だけ文字置換し、3902（旧数記載0）は必須補足のみ。元3901/781/24730 case説明は歴史byteのまま保持し、PG24744-current-component296-correction-v1/manifest.jsonとnamed-shapes.jsonを必須補足とする。製品・実120・84method/20Source参照・WBS受入/coverage/費用に変更なし。\n';p.write_text(corrected);active.append(dict(path=r['path'],beforeSha256=r['sha256'],sha256=sha(p),replacedOldLiteralCount=r['old295Occurrences']))
assert len(active)==2
for r in frozen:assert sha(R/r['path'])==r['sha256']
O.mkdir();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
write(O/'named-shapes.json',[dict(type=name,layouts=layouts[name],independentFields=shape) for name,shape in sorted(shapes.items())])
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=n['productionCoreMain'],testSource=n['source'],bug='BUG-2552',crossExpansion='YKT-2276',currentNamedTypes=69,currentCanonicalComponents=component,currentOptionalComponents=optional,currentEmptyTypes=empty,currentPublicBindings=len(getters),existingActualCase=key,normalProof=dict(path=str(normal.relative_to(R)),sha256=sha(normal)),helper=dict(path=str(helper.relative_to(R)),sha256=sha(helper)),inputFixtures={str((D/p).relative_to(R)):sha(D/p) for p in ['named-types-ss323.tsv','fields-ui234-236.tsv','named-accessors-independent.tsv']},mandatorySupplementFor=frozen,correctedActiveDocuments=active,namedShapesSha256=sha(O/'named-shapes.json'),historical295GloballyReplaced=False,oldPostMethodCountsRemainValid=True,sourceRegistryAcceptedDelta=0,newAcceptance=0,newProductTests=0,productTestsExecuted=0,newJavaCompilerExecutions=0,newCoverageMeasurement=False,formalUpdated=False,effortRate=None,allBranchOraclesIndividuallyVerified=False,toolSha256=sha(Path(__file__)))
write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,types=69,components=component,optionals=optional,empty=empty,bindings=len(getters),correctedDocuments=len(active),frozenReferences=len(frozen),manifestSha256=sha(O/'manifest.json'))))
