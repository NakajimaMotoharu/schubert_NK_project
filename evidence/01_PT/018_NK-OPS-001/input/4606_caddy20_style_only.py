"""BUG3155: exact reversible fixture-only names/counter syntax/constants; original20 expectations stay."""
from pathlib import Path
import hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';oldp=b/'evidence/PG37124-caddy-finite-only-source-v1/manifest.json';f=json.loads(oldp.read_text());p=r/f['testPath'];old=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==f['shaAfter']
out=b/'evidence/PG37128-caddy-style-only-equivalence-v1';assert not out.exists();out.mkdir();(out/'source-before.txt').write_text(old)
edits=[('  private static final String FIXTURE_STATUS_0_0_FCBA6B28', '  private static final int POST_TLS_GUARD_OBSERVATION = 4;\n  private static final int SECOND_MANAGER_OBSERVATION = 2;\n  private static final String FIXTURE_STATUS_0_0_FCBA6B28'),('Map<String, String> manager = values();','Map<String, String> managerView = values();'),('ChildStartupContext.Observed actor = ACTOR;','ChildStartupContext.Observed actorView = ACTOR;'),('int sockets;','int socketReads;'),('return manager;','return managerView;'),('return actor;','return actorView;'),('return ++sockets == 1 ? before : after;','socketReads++;\n      return socketReads == 1 ? before : after;'),('if (++guards == failGuard)', 'guards++;\n      if (guards == failGuard)'),('if (++calls == failIo)', 'calls++;\n      if (calls == failIo)'),('f.guards == 4','f.guards == POST_TLS_GUARD_OBSERVATION'),('reads.incrementAndGet() == 2','reads.incrementAndGet() == SECOND_MANAGER_OBSERVATION')]
# Field accesses only; preserve manager()/actor() method calls and diagnostic event strings.
for obj in ['f','mutated','wrong']:
 for field in ['manager','actor']:
  pat=rf'\b{obj}\.{field}\b(?!\s*\()'
  for m in reversed(list(re.finditer(pat,old))):
   source=m.group();edits.append((source,source+'View'))
# De-duplicate repeated field substitutions; replace all precise non-call accesses with regex below.
edits=edits[:11];new=old
for a,c in edits:assert a in new;new=new.replace(a,c)
new=re.sub(r'\b(f|mutated|wrong)\.(manager|actor)\b(?!\s*\()',lambda m:m.group()+'View',new)
inverse=re.sub(r'\b(f|mutated|wrong)\.(managerView|actorView)\b',lambda m:m.group().removesuffix('View'),new)
for a,c in reversed(edits):assert c in inverse;inverse=inverse.replace(c,a)
assert inverse==old and len(re.findall(r'@Test\s+void',new))==20
p.write_text(new);v=dict(actualExit=0,testPath=f['testPath'],shaBefore=f['shaAfter'],shaAfter=hashlib.sha256(p.read_bytes()).hexdigest(),inverseWholeByteExact=True,inversePreservesFiniteOnlySource=True,originalWhole20OraclesPreserved=True,MainChanged=False,wholeTests=20,finiteOnlyProof=dict(path=str(oldp.relative_to(r)),sha256=hashlib.sha256(oldp.read_bytes()).hexdigest()),bug='BUG3155',horizontal='YKT2624',productTestsExecuted=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reversible=True,wholeTests=20,productTests=0)))
