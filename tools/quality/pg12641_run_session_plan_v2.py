"""Three same-value fixture names; inverse restores every original Test/helper token."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12641-run-session-plan-v2'
SPECS={
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorRunEnvironmentTest.java':[('int','UUID_WORD_BITS','64','bit < 64',1)],
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionOperationTokenV2Test.java':[('String','OPERATION_PURPOSE','"QSBREQ01"',None,9),('String','TOKEN_ARRAY_END','"}]}"',None,6)]}

def raw(t):return [m.group() for m in LEX.finditer(t) if not m.group().startswith(('//','/*'))]

def before():
 n=data.read_checked(data.BASE/'PG12618-memory-boundary-six-compile-v1/manifest.json','967ad00dfe1db5205d96530aac7da01d0b697ce9be29f61553c16db086c050e9')
 root=Path(n['jars']['batch']['path']).parent.parent.parent.parent
 old={p:(root/p).read_text() for p in SPECS}
 assert all(data.sha(t.encode())==n['begin']['inputHashes'][p] for p,t in old.items())
 return n,old

def declaration(kind,name,literal):return '  private static final '+kind+' '+name+' = '+literal+';\n'

def intended(old):
 result={}
 for p,defs in SPECS.items():
  t=old[p];decls=''
  for kind,name,literal,condition,count in defs:
   if condition:
    assert t.count(condition)==count;t=t.replace(condition,condition.rsplit(' ',1)[0]+' '+name)
   else:
    matches=[m for m in LEX.finditer(t) if m.group()==literal];assert len(matches)==count
    for match in reversed(matches):t=t[:match.start()]+name+t[match.end():]
   decls+=declaration(kind,name,literal)
  match=re.search(r'(?:final )?class '+Path(p).stem+r' \{\n',t);assert match
  result[p]=t[:match.end()]+decls+'\n'+t[match.end():]
 return result

def require(old,new):
 assert set(old)==set(new)
 for p,defs in SPECS.items():
  t=new[p]
  for kind,name,literal,condition,count in defs:
   decl=declaration(kind,name,literal);assert t.count(decl)==1;t=t.replace(decl,'')
   assert len(re.findall(r'\b'+name+r'\b',t))==count
   if condition:
    ref=condition.rsplit(' ',1)[0]+' '+name;assert t.count(ref)==count;t=t.replace(ref,condition)
   else:t=re.sub(r'\b'+name+r'\b',lambda _:literal,t)
  assert raw(t)==raw(old[p])

def emit():
 _,old=before();new=intended(old);require(old,new);patch='*** Begin Patch\n'
 for p in old:
  assert (data.ROOT/p).read_text()==old[p]
  patch+='*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in list(difflib.unified_diff(old[p].splitlines(),new[p].splitlines(),n=3))[2:])+'\n'
 return patch+'*** End Patch\n'

def main():
 invocation=capture(__file__);assert not OUT.exists();n,old=before();new={p:(data.ROOT/p).read_text() for p in old};require(old,new)
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p not in new)
 bads=[]
 for p,defs in SPECS.items():
  for kind,name,literal,_,_ in defs:
   decl=declaration(kind,name,literal);wrong='1' if kind=='int' else '"WRONG_VALUE"'
   for t in [new[p].replace(decl,'',1),new[p].replace(decl,declaration(kind,name,wrong),1),new[p].replace(name,'WRONG_SYMBOL',1)]:
    assert t!=new[p];bads.append({**new,p:t})
 for p in new:
  t=new[p].replace('@Test','@Disabled',1);assert t!=new[p];bads.append({**new,p:t})
 p=next(p for p in new if p.endswith('InspectorRunEnvironmentTest.java'));bad=new[p].replace('(bit - 64)','(bit - 63)',1);assert bad!=new[p];bads.append({**new,p:bad})
 p=next(p for p in new if p.endswith('SessionOperationTokenV2Test.java'));bad=new[p].replace('formatVersion','wrongVersion',1);assert bad!=new[p];bads.append({**new,p:bad})
 for bad in bads:
  try:require(old,bad)
  except AssertionError:pass
  else:raise AssertionError('changed original token contract accepted')
 spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2362_run環境SessionV2三役割命名_単体テスト仕様書.md'
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBeforeLiteral=n['source'],sourceBeforeResolved='915a8ed153b00d76a80164d36f9ce5b86d645046',invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in old],typedBoundaryCorrections=1,stringCorrections=2,totalCorrections=3,totalReferences=16,metadataNegativeVectors=len(bads),allMainAndOtherInputsUnchanged=True,originalTests=9,originalSuites=2,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
 if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
 else:assert not sys.argv[1:];main()
