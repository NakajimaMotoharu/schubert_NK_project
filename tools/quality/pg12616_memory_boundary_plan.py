"""Independent inverse for three typed condition bounds; complete original Test tokens retained."""
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12616-memory-boundary-plan-v1'
SPECS={
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDbCredentialTest.java': [('MAX_INPUT_BYTES','65536','bytes.length > 65536')],
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/WebCsrfTokenTest.java': [('MIN_TOKEN_LENGTH','64','length > 64'),('MAX_TOKEN_LENGTH','128','length < 128')]}

def raw(t):return [m.group() for m in LEX.finditer(t) if not m.group().startswith(('//','/*'))]

def before():
 n=data.read_checked(data.BASE/'PG12592-public-claim-six-compile-v1/manifest.json','11866f6596012549a85e43d0ff9a0b9577f446dccb00ff9ecaeadce127d1e305')
 root=Path(n['jars']['batch']['path']).parent.parent.parent.parent
 old={p:(root/p).read_text() for p in SPECS}
 assert all(data.sha(t.encode())==n['begin']['inputHashes'][p] for p,t in old.items())
 return n,old

def require(old,new):
 assert set(old)==set(new)
 for p,definitions in SPECS.items():
  t=new[p]
  for name,value,condition in definitions:
   decl='  private static final int '+name+' = '+value+';\n'
   assert t.count(decl)==1;t=t.replace(decl,'')
   expected=condition.rsplit(' ',1)[0]+' '+name
   assert t.count(expected)==1 and len(re.findall(r'\b'+name+r'\b',t))==1
   t=t.replace(expected,condition)
  assert raw(t)==raw(old[p])

def main():
 invocation=capture(__file__);assert not OUT.exists();n,old=before();new={p:(data.ROOT/p).read_text() for p in old};require(old,new)
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p not in new)
 negatives=[]
 for p,defs in SPECS.items():
  for name,value,_ in defs:
   decl='  private static final int '+name+' = '+value+';\n'
   for t in [new[p].replace(decl,'',1),new[p].replace(decl,decl.replace(' = '+value,' = 1'),1),new[p].replace(name,'WRONG_BOUNDARY',1)]:
    assert t!=new[p];negatives.append({**new,p:t})
 for p in new:
  t=new[p].replace('@Test','@Disabled',1);assert t!=new[p];negatives.append({**new,p:t})
 for bad in negatives:
  try:require(old,bad)
  except AssertionError:pass
  else:raise AssertionError('changed original Test accepted')
 spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2360_メモリ入力CSRF二Test三境界命名_単体テスト仕様書.md'
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=n['source'],invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in old],typedBoundaryCorrections=3,conditionReferences=3,metadataNegativeVectors=len(negatives),allMainAndOtherInputsUnchanged=True,originalTests=8,originalSuites=2,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
