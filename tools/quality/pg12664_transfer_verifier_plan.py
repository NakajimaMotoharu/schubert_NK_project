"""Explicit finally-only owner change plus two fixture names; restore all original Test tokens."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12664-transfer-verifier-plan-v1'
PATH='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/TransferContentVerifierTest.java'
OLD_BLOCK='''    var closed = new TestInput(golden, 0);
    closed.close();
    reject(() -> TransferContentVerifier.verify(closed, expected));
    assertFalse(closed.isOpen());
'''
NEW_BLOCK='''    var closed = new TestInput(golden, 0);
    try {
      closed.close();
      reject(() -> TransferContentVerifier.verify(closed, expected));
      assertFalse(closed.isOpen());
    } finally {
      closed.close();
    }
'''
DECL='    private static final int ZERO_PROGRESS_MODE = 1;\n'

def raw(t):return [m.group() for m in LEX.finditer(t) if not m.group().startswith(('//','/*'))]

def before():
 n=data.read_checked(data.BASE/'PG12642-run-session-six-compile-v1/manifest.json','9444de936bee333dcc73a34419b26213a423a4ef02ea8be5e984d3612b12b629')
 root=Path(n['jars']['api']['path']).parent.parent.parent.parent;t=(root/PATH).read_text();assert data.sha(t.encode())==n['begin']['inputHashes'][PATH]
 return n,t

def rename(t,a,b,count):
 matches=[m for m in LEX.finditer(t) if m.group()==a];assert len(matches)==count
 for m in reversed(matches):t=t[:m.start()]+b+t[m.end():]
 return t

def intended(old):
 assert old.count(OLD_BLOCK)==1;t=old.replace(OLD_BLOCK,NEW_BLOCK);t=rename(t,'TestInput','ChunkedInput',8)
 head='  private static final class ChunkedInput implements ReadableByteChannel {\n';assert t.count(head)==1
 t=t.replace(head,head+DECL+'\n');assert t.count('if (mode == 1)')==1;t=t.replace('if (mode == 1)','if (mode == ZERO_PROGRESS_MODE)')
 return t

def require(old,new):
 assert new.count(DECL)==1;t=new.replace(DECL,'');assert len(re.findall(r'\bZERO_PROGRESS_MODE\b',t))==1 and t.count('if (mode == ZERO_PROGRESS_MODE)')==1
 t=t.replace('if (mode == ZERO_PROGRESS_MODE)','if (mode == 1)');t=rename(t,'ChunkedInput','TestInput',8)
 assert t.count(NEW_BLOCK)==1;t=t.replace(NEW_BLOCK,OLD_BLOCK);assert raw(t)==raw(old)

def emit():
 _,old=before();new=intended(old);require(old,new);assert (data.ROOT/PATH).read_text()==old
 return '*** Begin Patch\n*** Update File: '+str(data.ROOT/PATH)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=3))[2:])+'\n*** End Patch\n'

def main():
 invocation=capture(__file__);assert not OUT.exists();n,old=before();new=(data.ROOT/PATH).read_text();require(old,new)
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p!=PATH)
 bads=[new.replace(DECL,'',1),new.replace(DECL,DECL.replace(' = 1',' = 0'),1),new.replace('ChunkedInput','WrongInput',1),new.replace('if (mode == ZERO_PROGRESS_MODE)','if (mode != ZERO_PROGRESS_MODE)',1),new.replace('    } finally {\n      closed.close();\n    }','    } finally {\n    }',1),new.replace('assertEquals(4800, input.offset);','assertEquals(4799, input.offset);',1),new.replace('new int[] {1, 201, 10000}','new int[] {1, 200, 10000}',1),new.replace('@Test','@Disabled',1)]
 for bad in bads:
  assert bad!=new
  try:require(old,bad)
  except AssertionError:pass
  else:raise AssertionError('non-owner or altered original Test accepted')
 spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2364_TransferVerifier所有fixture三是正_単体テスト仕様書.md'
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=n['source'],invocation=invocation,sourceChanges=[dict(path=PATH,beforeSha256=data.sha(old.encode()),sha256=data.sha(new.encode()))],totalCorrections=3,renamedIdentifierReferences=8,typedConditionReferences=1,finallyOwnerOnlyChange=True,metadataNegativeVectors=len(bads),allMainAndOtherInputsUnchanged=True,originalTests=3,originalSuites=1,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
 if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
 else:assert not sys.argv[1:];main()
