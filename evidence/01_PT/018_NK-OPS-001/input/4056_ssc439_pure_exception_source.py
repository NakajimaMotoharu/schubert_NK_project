"""Remove only unused namespace instances; keep original20, add independent closed Reason contract."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pub=ld(b/'evidence/PG35252-ssc439-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC439';fmt=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];mains=[];inverse={}
for name in ['MorningSqlFailures','JdbcResourceFailures']:
 p=r/('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'+name+'.java');old=p.read_bytes();assert old==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);before='final class '+name+' {\n  private '+name+'() {}\n\n';after='interface '+name+' {\n';assert old.decode().count(before)==1;p.write_text(old.decode().replace(before,after,1));subprocess.run(fmt+['--replace',str(p)],check=True,timeout=30);value=p.read_text().replace(after,before,1);v=subprocess.run(fmt+['-'],input=value.encode(),capture_output=True,timeout=30);assert v.returncode==0 and v.stdout==old;inverse[name]=dict(oldSha256=hashlib.sha256(old).hexdigest(),newSha256=sha(p),methodBodiesInverseFormattedExact=True);mains.append(str(p.relative_to(r)))
for n in ['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRepositoryException.java','src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java']:assert (r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]);mains.append(n)
tests=[]
for name,count in [('MorningSqlFailuresTest',12),('JdbcResourceFailuresTest',8)]:
 n='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/'+name+'.java';assert (r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]);tests.append(dict(path=n,tests=count))
test='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StorageReasonValueContractTest.java';p=r/test;assert not p.exists();p.open('x').write('''package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-STORAGE-REASON001; SS333/354 SSC439: fixed public catalog, never storage or DB operations. */
final class StorageReasonValueContractTest {
  @Test
  void reason001ClosedCatalogFactoryAndRedactedFailureKeepTheirIndependentLiteralContract() {
    String[] names = {"COLLISION", "MISSING", "UNAVAILABLE"};
    StorageIoException.Reason[] reasons = StorageIoException.Reason.values();
    assertArrayEquals(names, Arrays.stream(reasons).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < names.length; index++) {
      StorageIoException.Reason reason = reasons[index];
      assertEquals(index, reason.ordinal());
      assertEquals(names[index], reason.name());
      assertSame(reason, StorageIoException.Reason.valueOf(names[index]));
      StorageIoException failure = new StorageIoException(reason);
      assertSame(reason, failure.reason());
      assertEquals("transfer storage operation failed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    StorageIoException.Reason[] copy = StorageIoException.Reason.values();
    assertNotSame(reasons, copy);
    copy[0] = null;
    assertSame(StorageIoException.Reason.COLLISION, StorageIoException.Reason.values()[0]);
    for (String unknown : List.of("", "collision", "COLLISION ", "UNKNOWN")) {
      assertThrows(IllegalArgumentException.class, () -> StorageIoException.Reason.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> StorageIoException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
  }
}
''');subprocess.run(fmt+['--replace',str(p)],check=True,timeout=30);tests.append(dict(path=test,tests=1));witnessp=b/'evidence/PG35250-ssc439-pure-exception-design-only-v1/ten-static-callers-source-witness.json';witness=ld(witnessp);assert len(witness['callers'])==10 and all(sha(r/x['path'])==x['sha256'] for x in witness['callers']);inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={n:next(x for x in inv['artifacts'] if x['path']==n)['owner'] for n in mains};e=b/'evidence/PG35254-ssc439-pure-exception-source-v1';e.mkdir();v=dict(actualExit=0,designPublication=pub,mainSources=mains,testSources=tests,expectedTests=21,newTestDefinitions=1,necessaryPriorDefinitions=20,originalTwentyTestsByteExact=True,onlyTwoDeclarationAndEmptyCtorInverseExact=inverse,unchangedStorageAndCatalogSource=True,tenCallerSourceWitness=dict(path=str(witnessp.relative_to(r)),sha256=sha(witnessp)),oldCallerBinaryReuseAllowed=False,fullTenCallerRebuiltAndQualified=False,inputHashes={n:sha(r/n) for n in mains+[x['path'] for x in tests]},productOwnerByMainPath=owners,targets=['dev/codex/schubert/nk/batch/repository/'+n for n in ['MorningSqlFailures','JdbcResourceFailures','BatchRepositoryException']]+['dev/codex/schubert/nk/storage/StorageIoException','dev/codex/schubert/nk/storage/StorageIoException$Reason'],actualBackendOrHeldOrAuthorityActions=0,applicationTestsExecuted=0);(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=len(mains),tests=21,newDefinitions=1,originalTwentyByteExact=True,inverseExact=True)))
