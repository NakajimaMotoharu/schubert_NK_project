"""Finite whole5 fixture with one real pure lexical Main; no credential/environment/file access."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29630-location-five-finite-source-oracle-v1';o.mkdir();main='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ServiceCredentialLocation.java';test=main.replace('/main/','/test/').replace('.java','Test.java');p=r/test;old=p.read_text();(o/'ServiceCredentialLocationTest.before.java.txt').write_text(old)
pairs=[('import static org.junit.jupiter.api.Assertions.assertThrows;','import static org.junit.jupiter.api.Assertions.assertThrows;\nimport static org.junit.jupiter.api.Assertions.assertTrue;'),('    try (var pool = Executors.newFixedThreadPool(8)) {','    var pool = Executors.newFixedThreadPool(8);\n    try {'),('''      for (var task : tasks) assertEquals(expected, task.get(10, TimeUnit.SECONDS));
    }
  }''','''      for (var task : tasks) assertEquals(expected, task.get(10, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS), "fixture workers not stopped");
    }
  }''')];new=old
for x,z in pairs:assert new.count(x)==1;new=new.replace(x,z)
inverse=new
for x,z in reversed(pairs):assert inverse.count(z)==1;inverse=inverse.replace(z,x)
assert inverse==old and old.count('@Test')==new.count('@Test')==5
p.write_text(new);tc=r.parent/'toolchain';fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(fmt+['--replace',str(p)],check=True,capture_output=True);norm=lambda s:subprocess.check_output(fmt+['-'],input=s.encode());assert norm(inverse)==norm(old) and p.read_bytes()==norm(new)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));text=(r/main).read_text();assert all(x not in text+new for x in ['System.getenv','Files.','newDirectoryStream','ServiceConfigFiles','java.lang.foreign','Class.forName','DataSource','java.net.'])
proof=dict(actualExit=0,productionCoreMain='5330eb303026206a87af466d0ffebb884b8e04b8',wholeOriginalTests=5,newDefinitions=0,oldWholeFiveNormalizedInverseEqual=True,MainChanged=False,testBeforeSha256=hashlib.sha256(old.encode()).hexdigest(),testAfterSha256=sha(p),inputHashes={main:sha(r/main)},wholeSourceClosure='ONE_REAL_SERVICE_CREDENTIAL_LOCATION_JDK_MAP_PATH_METADATA; NO_REAL_ENV_FS_CREDENTIAL_NATIVE_ROOT_AUTHORITY',fixedFixtureChanges=['samepool8/tasks32/get10 retained','finallyshutdownNow+awaitTermination10true'],productTestsExecuted=0,actualPrivateOrHeldOperations=0)
(o/'manifest.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
c=json.loads((b/'input/2310_attempt8_closed_profile.json').read_text());c.update(id='PG29640-LOCATION-ORIGINAL-WHOLE5-FINITE-OWNER',productionCoreMain=proof['productionCoreMain'],productOwnerByMainPath={main:'WBS-P003-07'},oracleSpecs=[ref(r/'evidence/01_PT/003_NK-PRO-003/4145_ServiceCredentialLocation原五件・有限worker単体仕様.md')],closureProofs=[ref(o/'manifest.json')],mainSources=[main],testSources=[dict(path=test,tests=5)],expectedTests=5,resources=[],systemProperties={},physicalClasses=['dev/codex/schubert/nk/storage/ServiceCredentialLocation.class'],targetClasses=['dev/codex/schubert/nk/storage/ServiceCredentialLocation'],pomInputs=['pom.xml','src/schubert-nk-storage/pom.xml']);ids=dict(prestyle=29632,prepare=29634,static=29636,preflight=29638,unit=29640,post=29642);c['slots']={k:'evidence/01_PT/018_NK-OPS-001/evidence/PG'+str(v)+'-location5-'+k+'-v1' for k,v in ids.items()};c['privateDirs']={k:'pg'+str(ids[k])+'-location5-'+k+'-v1' for k in ['prepare','unit']};dst=b/'input/2367_location5_closed_profile.json';assert not dst.exists();dst.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print('whole5 oldoracles inverse-equal; onepureMain/noenvfiles/native; exactStoragePOM; newdefinitions0')
