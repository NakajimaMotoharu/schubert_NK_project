"""BUG2767 finite worker only; all original oracles preserved. No Product run."""
from pathlib import Path
import json,hashlib,subprocess,datetime,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';sys.path.insert(0,str(R/'tools/quality'));import pg9666_pagination_static as steps
c=json.loads((B/'input/2149_mq31_normal_start.json').read_text());p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisParentDeadlineTest.java';old=subprocess.check_output(['git','show','dd0a503eadfb4499a5d3e8a0fc3d8cc929d55897:'+str(p.relative_to(R))],text=True);assert p.read_text()==old;new=old;inverse=[]
def rep(a,b):
 global new
 assert new.count(a)==1;new=new.replace(a,b);inverse.append((b,a))
rep('import static org.junit.jupiter.api.Assertions.assertEquals;\n','import static org.junit.jupiter.api.Assertions.assertEquals;\nimport static org.junit.jupiter.api.Assertions.assertFalse;\n')
rep('          thread.start();\n','          thread.setDaemon(true);\n          thread.start();\n')
rep('''          try {
            thread.join();
          } catch (InterruptedException known) {
            throw new AssertionError(known);
          }
''','''          try {
            await(thread);
          } finally {
            thread.interrupt();
            await(thread);
          }
          assertFalse(thread.isAlive(), "bounded independent worker must terminate");
''')
helper='''
  private static void await(Thread worker) {
    try {
      worker.join(10_000);
    } catch (InterruptedException known) {
      Thread.currentThread().interrupt();
      throw new AssertionError(known);
    }
  }
''';assert new.endswith('}\n');new=new[:-2]+helper+'}\n';inverse.append((helper,''));p.write_text(new)
O=B/'evidence/PG28526-mq31-original-worker-and-new5-source-v1';assert not O.exists();O.mkdir();steps.SLOT=O;stages={}
paths=[p,R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisCatalogFatalBoundaryTest.java']
for q in paths:
 label='format-'+q.stem;stages[label]=steps.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(q)],R);assert stages[label]['actualExit']==0
reverse=p.read_text()
for add,remove in reversed(inverse):assert reverse.count(add)==1;reverse=reverse.replace(add,remove)
assert reverse==old;sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore='dd0a503eadfb4499a5d3e8a0fc3d8cc929d55897',productionCoreMain=c['source'],original26AssertionsAndWorkerOracleInverseExact=True,finiteWorker=dict(source=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),joinMillis=10000,finallyInterruptAndBoundedJoin=True,daemonOnTimeoutPreventsUnboundedJvm=True,aliveMustBeFalse=True,normal26TestsNotExecuted=True),newTestDefinitions=5,newTestPath=str(paths[1].relative_to(R)),newTestSha256=sha(paths[1]),stages=stages,productTestsExecuted=0,MainChanged=False);(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,original26InverseExact=True,newDefinitions=5,productTestsExecuted=0)))
