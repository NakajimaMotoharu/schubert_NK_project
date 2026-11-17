"""Source-only Web enum direct contract candidate inventory; no dynamic class loading or proof PASS."""
from pathlib import Path
import re,json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';src=r/'src/schubert-nk-web/src/main/java';testroot=r/'src/schubert-nk-web/src/test/java';rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tests=[]
for p in testroot.rglob('*.java'):
 t=p.read_text();tests.append((p,t))
for p in src.rglob('*.java'):
 t=p.read_text();package=re.search(r'package ([\w.]+);',t)
 if not package:continue
 for m in re.finditer(r'\benum\s+(\w+)',t):
  enum=m.group(1);outer=p.stem;qualified=package.group(1)+'.'+(enum if enum==outer else outer+'.'+enum);refs=[]
  for q,s in tests:
   samepackage=('package '+package.group(1)+';') in s
   context=qualified in s or (samepackage and outer+'.'+enum in s)
   # An imported nested enum permits an unqualified direct enum name.
   imported=('import '+qualified+';') in s
   if not context and not imported:continue
   calls=[]
   for n,line in enumerate(s.splitlines(),1):
    if re.search(r'\b'+re.escape(outer+'.'+enum)+r'\.(?:values|valueOf)\s*\(',line) or imported and re.search(r'\b'+re.escape(enum)+r'\.(?:values|valueOf)\s*\(',line):calls.append(dict(line=n,values='values(' in line,valueOf='valueOf(' in line))
   refs.append(dict(path=str(q.relative_to(r)),sha256=sha(q),directCallCandidates=calls,fixtureAuthorityAndOracleQualification='NOT_INFERRED_FROM_SOURCE',executionClaim=False))
  status='CURRENT_MEDIA9_POST_PENDING' if qualified.endswith('WebMediaAudit.Failure') else 'EXISTING_RAW_ENUM2_BYTE_BIND_PENDING' if '.WebSecurityAudit.' in qualified else 'EXISTING_PROOF_OR_PERMITTED_PG_PT_STILL_REQUIRED'
  rows.append(dict(source=str(p.relative_to(r)),sha256=sha(p),enum=qualified,line=t[:m.start()].count('\n')+1,testSourceCandidates=refs,directValueOfCandidateFiles=sum(any(a['valueOf'] for a in x['directCallCandidates']) for x in refs),status=status,globalHoldUnchanged=True,formalAccepted=False))
assert len(rows)==29
out=b/'evidence/PG37485-web-enum29-source-inventory-v1';assert not out.exists();out.mkdir();(out/'web-enum29.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),enumDeclarations=29,ownMedia1=1,security2=2,otherDeclarations26=26,otherWithDirectValueOfCandidate=sum(x['directValueOfCandidateFiles']>0 for x in rows if x['status']=='EXISTING_PROOF_OR_PERMITTED_PG_PT_STILL_REQUIRED'),allRowsAreSourceCandidatesNotPass=True,productTestsExecuted=0,heldClassfilesOrActualRootVmDbKeysRead=False,sourceInventorySha256=sha(out/'web-enum29.json'),ykt='YKT2645',yktComplete=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print({k:v[k] for k in ['actualExit','enumDeclarations','otherDeclarations26','otherWithDirectValueOfCandidate','yktComplete']})
