"""Read only original public ledger and known public manifests, never product/source execution."""
from pathlib import Path
import json,re,hashlib,subprocess,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33700-ledger-second26-catalog-v1';assert not e.exists();e.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head='84467c681ebf2c905879147c1c113f4b48ba3f96';path='documents/900_OTHER/910_台帳/915_障害表.md';text=subprocess.check_output(['git','show',head+':'+path],text=True);sections={int(m.group(1)):m.group(0) for m in re.finditer(r'^## BUG-(\d+)\b.*?(?=^## BUG-|\Z)',text,re.M|re.S)};opens={n:s for n,s in sections.items() if re.search(r'状態OPEN|状態[:：]\s*(?:OPEN|未解決|調査中|対応中)',s)};assert len(opens)==225
def bug_ids(value):
 out=set()
 for m in re.finditer(r'BUG-?(\d{3,4})((?:/\d{3,4})*)(?![0-9])',value):
  out.add(int(m.group(1)));out.update(int(x) for x in re.findall(r'/([0-9]+)',m.group(2)))
 for m in re.finditer(r'BUG-?(\d{3,4})(?:\.\.|[～〜~-])(?:BUG-?)?(\d{3,4})(?![0-9])',value):
  first,last=map(int,m.groups())
  if first<=last and last-first<=100:out.update(range(first,last+1))
 return out
def pg_ids(value):return sorted(set(map(int,re.findall(r'PG(\d{3,5})(?![0-9])',value))))
def closure_subjects(value):
 previous=0;out=set()
 for m in re.finditer(r'CLOSED(?=[:：（(、。]|$)',value):
  prefix=value[previous:m.start()]
  previous=m.end()
  if re.search(r'(?:未|NOT[_ -]?)$',prefix):continue
  out.update(bug_ids(prefix))
 return out
# Independent parser regression vectors. Tool-only assertions, never product PT credit.
assert pg_ids('PG31736全383/PG31738全35CRC')==[31736,31738]
assert pg_ids('PG123456不可')==[]
assert pg_ids('xPG31736/PG31736')==[31736]
assert bug_ids('BUG2912/2914/2915')=={2912,2914,2915}
assert bug_ids('BUG-2908..2910')=={2908,2909,2910}
assert closure_subjects('BUG2911工具限定CLOSED: proof。BUG2912/YKT2442・BUG2914/YKT2444 Test限定CLOSED: proof')=={2911,2912,2914}
assert closure_subjects('BUG2913 NOT_CLOSED: 保留')==set()
assert closure_subjects('BUG2915 CLOSEDはしない')==set()
eligible=lambda value:re.match(r'^20[0-9]{2}-[0-9]{2}-[0-9]{2} BUG-?[0-9]',value) is not None
assert eligible('2026-11-14 BUG2908/YKT2438 限定CLOSED: proof')
assert not eligible('対象helper。原因は既BUG2908。状態CLOSED（PG32308限定）')
closures={}
for para in re.split(r'\n\s*\n',text):
 if not eligible(para):continue
 for n in closure_subjects(para):closures.setdefault(n,[]).append(para)
# Directory-name inventory only; no private/raw/class/artifact payload reads.
dirs={}
for p in (b/'evidence').iterdir():
 m=re.match(r'PG(\d+)-',p.name)
 if m:dirs.setdefault(int(m.group(1)),[]).append(p)
target_ids=set(json.loads((b/'input/3402_ledger_second26_plan.json').read_text())['targetBugIds'])
rows=[];checked={}
for n,s in opens.items():
 ps=closures.get(n,[]);target=n in target_ids;row=dict(bug=n,title=s.splitlines()[0],originalSectionSha256=hashlib.sha256(s.encode()).hexdigest(),inCurrentBoundedMigrationReview=target,explicitClosureParagraphs=len(ps),status='PENDING_SCOPE_REVIEW' if ps else 'OPEN_NO_EXPLICIT_CLOSURE_IDENTIFIED',originalStatePreserved=True)
 if target:
  p=ps[-1] if ps else s
  refs=pg_ids(p+"\n"+s);proof=[]
  for num in refs:
   for folder in dirs.get(num,[]):
    f=folder/'manifest.json'
    if not f.is_file():continue
    try:x=json.loads(f.read_text())
    except (ValueError,UnicodeError):continue
    key=str(f.relative_to(r));record=dict(path=key,sha256=sha(f),actualExit=x.get('actualExit'),source=x.get('source') or x.get('actualUnitSource'),tests=x.get('tests') or x.get('productTestsExecuted'),keys=sorted(x.keys()),wholeScopeFour100=x.get('wholeScopeFour100'),rawFour100=x.get('rawFour100'))
    checked[key]=record;proof.append(record)
  row.update(originalSection=s,closureParagraph=p,closureIsDatedExplicit=bool(ps),closureParagraphSha256=hashlib.sha256(p.encode()).hexdigest(),mentionedPgIds=refs,originalPublicManifestRefs=proof,proofScope='HISTORICAL_EXPLICIT_LIMITED_CLOSURE_ONLY_NOT_FORMAL_REACCEPTANCE')
 rows.append(row)
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalHead=head,originalLedgerPath=path,originalLedgerGitBlobSha256=hashlib.sha256(text.encode()).hexdigest(),candidates=rows,candidateCount=225,boundedTargetIds=[x['bug'] for x in rows if x['inCurrentBoundedMigrationReview']],publicManifestsChecked=len(checked),independentToolParserChecks=10,originalCatalogPreserved=True,productTestsExecuted=0,sourceRuntimeVmDbNativeOrHeldActions=0,formalAcceptanceChanged=False,ledgerWritten=False)
(e/'candidate-catalog.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,candidates=225,targetCount=len(out['boundedTargetIds']),targets=[dict(bug=x['bug'],closures=x['explicitClosureParagraphs'],manifests=len(x.get('originalPublicManifestRefs',[])),successfulManifests=sum(p['actualExit']==0 for p in x.get('originalPublicManifestRefs',[]))) for x in rows if x['inCurrentBoundedMigrationReview']],ledgerWritten=False))
