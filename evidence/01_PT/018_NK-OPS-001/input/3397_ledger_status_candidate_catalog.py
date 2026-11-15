"""Read only original public ledger and known public manifests, never product/source execution."""
from pathlib import Path
import json,re,hashlib,subprocess,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33690-ledger-status-original-proof-v1';assert not e.exists();e.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head='84467c681ebf2c905879147c1c113f4b48ba3f96';path='documents/900_OTHER/910_台帳/915_障害表.md';text=subprocess.check_output(['git','show',head+':'+path],text=True);sections={int(m.group(1)):m.group(0) for m in re.finditer(r'^## BUG-(\d+)\b.*?(?=^## BUG-|\Z)',text,re.M|re.S)};opens={n:s for n,s in sections.items() if re.search(r'状態OPEN|状態[:：]\s*(?:OPEN|未解決|調査中|対応中)',s)};assert len(opens)==225
closures={}
for para in re.split(r'\n\s*\n',text):
 if 'CLOSED' not in para:continue
 prefix=para[:para.index('CLOSED')]
 if re.search(r'未CLOSED|NOT.?CLOSED',prefix[-30:]):continue
 ids=set(map(int,re.findall(r'BUG-?(\d{3,4})\b',prefix)))
 for n in ids:closures.setdefault(n,[]).append(para)
# Directory-name inventory only; no private/raw/class/artifact payload reads.
dirs={}
for p in (b/'evidence').iterdir():
 m=re.match(r'PG(\d+)-',p.name)
 if m:dirs.setdefault(int(m.group(1)),[]).append(p)
rows=[];checked={}
for n,s in opens.items():
 ps=closures.get(n,[]);target=2900<=n<=2925;row=dict(bug=n,title=s.splitlines()[0],originalSectionSha256=hashlib.sha256(s.encode()).hexdigest(),inCurrentBoundedMigrationReview=target,explicitClosureParagraphs=len(ps),status='PENDING_SCOPE_REVIEW' if ps else 'OPEN_NO_EXPLICIT_CLOSURE_IDENTIFIED',originalStatePreserved=True)
 if target and ps:
  p=ps[-1];refs=sorted(set(map(int,re.findall(r'\bPG(\d{3,5})\b',p))));proof=[]
  for num in refs:
   for folder in dirs.get(num,[]):
    f=folder/'manifest.json'
    if not f.is_file():continue
    try:x=json.loads(f.read_text())
    except (ValueError,UnicodeError):continue
    key=str(f.relative_to(r));record=dict(path=key,sha256=sha(f),actualExit=x.get('actualExit'),source=x.get('source') or x.get('actualUnitSource'),tests=x.get('tests') or x.get('productTestsExecuted'),keys=sorted(x.keys()),wholeScopeFour100=x.get('wholeScopeFour100'),rawFour100=x.get('rawFour100'))
    checked[key]=record;proof.append(record)
  row.update(closureParagraph=p,closureParagraphSha256=hashlib.sha256(p.encode()).hexdigest(),mentionedPgIds=refs,originalPublicManifestRefs=proof,proofScope='HISTORICAL_EXPLICIT_LIMITED_CLOSURE_ONLY_NOT_FORMAL_REACCEPTANCE')
 rows.append(row)
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalHead=head,originalLedgerPath=path,originalLedgerGitBlobSha256=hashlib.sha256(text.encode()).hexdigest(),candidates=rows,candidateCount=225,boundedTargetIds=[x['bug'] for x in rows if x['inCurrentBoundedMigrationReview']],publicManifestsChecked=len(checked),productTestsExecuted=0,sourceRuntimeVmDbNativeOrHeldActions=0,formalAcceptanceChanged=False,ledgerWritten=False)
(e/'candidate-catalog.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,candidates=225,targetCount=len(out['boundedTargetIds']),targets=[dict(bug=x['bug'],closures=x['explicitClosureParagraphs'],manifests=len(x.get('originalPublicManifestRefs',[])),successfulManifests=sum(p['actualExit']==0 for p in x.get('originalPublicManifestRefs',[]))) for x in rows if x['inCurrentBoundedMigrationReview']],ledgerWritten=False))
