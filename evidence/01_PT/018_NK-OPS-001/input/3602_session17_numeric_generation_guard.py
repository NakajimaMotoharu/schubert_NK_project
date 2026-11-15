"""Independently compare all integer AST leaves in the three generated tools and check all194 headers."""
from pathlib import Path
import ast,hashlib,json
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pairs=[('3557_ssc423_hash6_run.py','3597_session_issue_audit17_run.py'),('3558_ssc423_hash6_independent_post.py','3598_session_issue_audit17_independent_post.py'),('3559_ssc423_hash6_unfiltered.py','3599_session_issue_audit17_unfiltered_v2.py')]
def integers(source):return [n.value for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Constant) and type(n.value) is int]
checks=[];allowed={(180,194),(6,17),(3,0),(3,17),(1,2),(4,18)}
for old,new in pairs:
 a=integers((i/old).read_text());z=integers((i/new).read_text());assert len(a)==len(z) and 179 not in z
 changed=[dict(index=n,before=v,after=w) for n,(v,w) in enumerate(zip(a,z)) if v!=w];assert all((v['before'],v['after']) in allowed for v in changed)
 for v,w in zip(a,z):
  if v==69:assert w==69
 checks.append(dict(before=ref(i/old),after=ref(i/new),intLeaves=len(a),changed=changed,fixedMajor69Preserved=True))
original=integers((i/'3599_session_issue_audit17_unfiltered.py').read_text());corrected=integers((i/'3599_session_issue_audit17_unfiltered_v2.py').read_text());assert len(original)==len(corrected) and [(a,z) for a,z in zip(original,corrected) if a!=z]==[(179,69)]
m=ld(b/'evidence/PG33974-session-issue-audit17-prepare-v1/manifest.json');names=list(m['physicalClassHashes']);assert len(names)==194
for name in names:policy.relative_name(name)
root=r.parent/'pgpt-runs/PG379/pg33974-session-issue-audit17-v1/component';majors={}
for name in names:
 data=(root/name).read_bytes();assert hashlib.sha256(data).hexdigest()==m['physicalClassHashes'][name];major=int.from_bytes(data[6:8],'big');assert major==69;majors[name]=major
out=b/'evidence/PG33995-session17-numeric-generation-guard-v1';assert not out.exists();out.mkdir();(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,checks=checks,narrowV2OnlyMajor179To69=True,actual194HeadersAll69=True,majors=majors,allPhysicalHashesUnchanged=True,applicationTestsExecuted=0,analyzerExecuted=0,originalUnitAndPostReplayed=False,bug='BUG3032',horizontal='YKT2552'),indent=2)+'\n');print(json.dumps(dict(actualExit=0,tools=3,majorHeaders=194,actualMajor=69,onlyV2LiteralCorrection=True)))
