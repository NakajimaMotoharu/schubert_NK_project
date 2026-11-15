"""Repair exactly two old worker lifetimes, retaining business assertions by reversible edits."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/ContextHashTest.java';old=p.read_text();s=old;changes=[]
a='try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {';z='var executor = Executors.newVirtualThreadPerTaskExecutor();\n    try {';assert s.count(a)==2;s=s.replace(a,z);changes.append(dict(old=a,new=z,count=2))
a='futures.get(i).get()';z='futures.get(i).get(5, java.util.concurrent.TimeUnit.SECONDS)';assert s.count(a)==1;s=s.replace(a,z);changes.append(dict(old=a,new=z,count=1))
a='''      }
    }
  }

  @Test
  void asciiVectors''';z='''      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }

  @Test
  void asciiVectors''';assert s.count(a)==1;s=s.replace(a,z);changes.append(dict(old=a,new=z,count=1))
a='''futures.get(i).get(5, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertThrows''';z='''futures.get(i).get(5, java.util.concurrent.TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertThrows''';assert s.count(a)==1;s=s.replace(a,z);changes.append(dict(old=a,new=z,count=1))
imports='import static org.junit.jupiter.api.Assertions.assertTrue;\n';s=s.replace('import dev.codex.schubert.nk.protocol.header.AuthenticationContext;',imports+'\nimport dev.codex.schubert.nk.protocol.header.AuthenticationContext;');s=s.replace('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;');s=s.replace('final class ContextHashTest {','@Timeout(value = 20, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class ContextHashTest {')
reverse=s.replace(imports+'\n','').replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 20, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','')
for c in reversed(changes):assert reverse.count(c['new'])==c['count'];reverse=reverse.replace(c['new'],c['old'])
assert reverse==old and s.count('@Test')==3 and s.count('shutdownNow();')==s.count('assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));')==2
out=b/'evidence/PG33858-context-hash3-fixture-inverse-v1';assert not out.exists();out.mkdir();oldhash=hashlib.sha256(old.encode()).hexdigest();assert oldhash==json.loads((b/'input/3539_context_hash3_start.json').read_text())['oldInputHashes'][str(p.relative_to(r))];p.write_text(s)
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,path=str(p.relative_to(r)),sourceBefore=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),oldSha256=oldhash,changes=changes,rawAfterSha256=hashlib.sha256(s.encode()).hexdigest(),inverseOriginalExact=True,originalBusinessAssertionsUnchanged=True,originalProviderUnavailableBodyUnchanged=True,oldTestDefinitions=3,newTestDefinitions=0,applicationTestsExecuted=0,bug='BUG3026',horizontal='YKT2550'),indent=2)+'\n');print(json.dumps(dict(actualExit=0,originalAssertionsInverseExact=True,workerSites=2)))
