from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchStepValuesTest.java';old=p.read_text();opening='    try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {\n';newopening='    var pool = Executors.newVirtualThreadPerTaskExecutor();\n    try {\n';end='''        assertEquals(LocalDate.of(2026, 9, 13), a.businessDate());
      }
    }
  }
''';newend='''        assertEquals(LocalDate.of(2026, 9, 13), a.businessDate());
      }
    } finally {
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("owned virtual value workers did not terminate");
    }
  }
''';assert old.count(opening)==old.count(end)==1;new=old.replace(opening,newopening).replace(end,newend);assert new.replace(newopening,opening).replace(newend,end)==old;assert new.count('.get(5, TimeUnit.SECONDS)')==old.count('.get(5, TimeUnit.SECONDS)')==1;assert '## BUG-2746' in (R/'documents/900_OTHER/910_台帳/915_障害表.md').read_text();p.write_text(new);cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)];v=subprocess.run(cmd,capture_output=True);assert v.returncode==0 and p.read_text()==new
O=B/'evidence/PG28241-step8-finite-worker-source-v1';assert not O.exists();O.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),path=str(p.relative_to(R)),oldSha256=sha(old.encode()),newSha256=sha(new.encode()),bug='BUG2746',originalWhole8AndAllAssertionsPreserved=True,inverseExact=True,existingFutureSeconds=5,finallyShutdownNow=True,awaitSeconds=10,formatCommand=cmd,formatExit=0,MainChanged=False,productTestsExecuted=0),indent=2)+'\n');print(json.dumps(dict(actualExit=0,inverseExact=True,testsExecuted=0)))
