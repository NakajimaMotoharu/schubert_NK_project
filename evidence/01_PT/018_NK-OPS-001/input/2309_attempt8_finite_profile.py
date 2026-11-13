"""Preserve old whole8 golden and build exact immutable-data closure; no authority fixture."""
from pathlib import Path
import json,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29420-attempt8-finite-source-oracle-v1';assert not o.exists();o.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base=Path('src/schubert-nk-batch/src');test=base/'test/java/dev/codex/schubert/nk/batch/cleanup/InspectionAttemptTest.java';p=r/test;old=p.read_text();(o/'InspectionAttemptTest.before.java.txt').write_text(old)
pairs=[('import static org.junit.jupiter.api.Assertions.assertThrows;','import static org.junit.jupiter.api.Assertions.assertThrows;\nimport static org.junit.jupiter.api.Assertions.assertTrue;'),('    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {','    var executor = Executors.newVirtualThreadPerTaskExecutor();\n    try {'),('''        assertEquals(Outcome.WARNING, result.outcome());
      }
    }
  }
}''','''        assertEquals(Outcome.WARNING, result.outcome());
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "fixture workers not stopped");
    }
  }
}''')]
s=old
for a,z in pairs:assert s.count(a)==1;s=s.replace(a,z)
p.write_text(s);tc=r.parent/'toolchain';fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(fmt+['--replace',str(p)],check=True,capture_output=True);norm=lambda s:subprocess.check_output(fmt+['-'],input=s.encode());assert p.read_bytes()==norm(s);inverse=s
for a,z in reversed(pairs):assert inverse.count(z)==1;inverse=inverse.replace(z,a)
assert norm(inverse)==norm(old) and s.count('@Test')==old.count('@Test')==8
for forbidden in ['executor.shutdownNow();','executor.awaitTermination(10, TimeUnit.SECONDS)']:assert forbidden in s and forbidden not in old
mainbase=base/'main/java/dev/codex/schubert/nk/batch';mains=[mainbase/'cleanup/InspectionAttempt.java']+[mainbase/'repository'/n for n in ['BatchRun.java','CleanupCounts.java','InspectionSummary.java','MaintenanceCompletion.java','MaintenanceActivation.java']];inv=json.loads((r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text());by={x['path']:x for x in inv['artifacts']};owners={str(x):by[str(x)].get('costOwner',by[str(x)].get('owner')) for x in mains};assert owners[str(mains[0])]=='WBS-P004-04'
m=dict(actualExit=0,productionCoreMain='bba3e0cd94e426e82bceec3182060c3695cd0ec6',MainChanged=False,wholeOriginalTests=8,newTestDefinitions=0,oldWholeOraclesNormalizedInverseEqual=True,testBeforeSha256=hashlib.sha256(old.encode()).hexdigest(),testAfterSha256=sha(p),pureWholeMainReviewed=6,inputHashes={str(x):sha(r/x) for x in mains},productOwnerByMainPath=owners,closure='JDK/JSpecify/JUnit pureimmutable records andnestedOutcome enum; notDB/child/Backup/activation/Root authority. EntireMaintenanceCompletion/Activation outerpublicsource included, no signature substitution.',productTestsExecuted=0,prohibitedActions=0);(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
c=json.loads((b/'input/2298b_env10_closed_profile.json').read_text());c.update(id='PG29432-INSPECTION-ATTEMPT-ORIGINAL-WHOLE8-FINITE-WORKER',productionCoreMain=m['productionCoreMain'],productOwnerByMainPath=owners,oracleSpecs=[ref(r/'evidence/01_PT/004_NK-DAT-001/4235_InspectionAttempt原八件・有限worker単体仕様.md')],closureProofs=[ref(o/'manifest.json')],mainSources=[str(x) for x in mains],testSources=[dict(path=str(test),tests=8)],expectedTests=8,resources=[],systemProperties={},physicalClasses=['dev/codex/schubert/nk/batch/cleanup/InspectionAttempt.class']+['dev/codex/schubert/nk/batch/repository/'+n+'.class' for n in ['BatchRun','CleanupCounts','InspectionSummary','MaintenanceCompletion','MaintenanceCompletion$Outcome','MaintenanceActivation']],targetClasses=['dev/codex/schubert/nk/batch/cleanup/InspectionAttempt']);ids=dict(prestyle=29424,prepare=29426,static=29428,preflight=29430,unit=29432,post=29434);c['slots']={k:'evidence/01_PT/018_NK-OPS-001/evidence/PG'+str(v)+'-attempt8-'+k+'-v1' for k,v in ids.items()};c['privateDirs']={k:'pg'+str(ids[k])+'-attempt8-'+k+'-v1' for k in ['prepare','unit']};dst=b/'input/2310_attempt8_closed_profile.json';assert not dst.exists();dst.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print('whole8 oldoracles preserved, Main6 physical7 JDKdata closure, exact batchPOM')
