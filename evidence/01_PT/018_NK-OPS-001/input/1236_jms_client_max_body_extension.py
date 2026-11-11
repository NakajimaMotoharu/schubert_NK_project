"""Before first compile: complete independently specified exact maximum-body boundary in new case only."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26448-jms-client-max-body-manufacture-v2';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=B/'evidence/PG26446-jms-client-manufacture-v1/manifest.json';v=json.loads(parent.read_bytes());assert sha(parent)=='60dcf42eb4ddd37b63fa211cf0648c66cb44507634b6f3e9b6a30a05a59251a3';p=R/v['testPath'];before=p.read_text();assert sha(p)==v['testSha256'];old="""    assertEquals(2, sends.get());
    assertEquals(0, registry.pendingCount());
  }

  // JMSCLIENT009010-END""";extra="""    byte[] maximum = new byte[1_000_000];
    assertArrayEquals(new byte[] {8}, client.exchange(ID_1, maximum, Duration.ofSeconds(2),
        (id, body) -> {
          sends.incrementAndGet();
          assertEquals(1_000_000, body.length);
          body[0] = 9;
          assertTrue(client.onReply(id, new byte[] {8}));
        }));
    assertEquals(0, maximum[0]);
    assertEquals(3, sends.get());
    assertEquals(0, registry.pendingCount());
"""
# google-java-format inserts no blank line before the ending comment if source already contains one.
if old not in before:
 old=old.replace('  }\n\n  //','  }\n  //')
assert before.count(old)==1;first='    assertEquals(2, sends.get());\n    assertEquals(0, registry.pendingCount());\n';new=first+extra+old[len(first):];s=before.replace(old,new,1);assert s.replace(new,old,1)==before;cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'-'];run=subprocess.run(cmd,input=s.encode(),capture_output=True,timeout=30);assert run.returncode==0;fixed=run.stdout;again=subprocess.run(cmd,input=fixed,capture_output=True,timeout=30);assert again.returncode==0 and again.stdout==fixed;O.mkdir();(O/'parent-whole-test.java.txt').write_text(before);p.write_bytes(fixed);d=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),parentManufactureSha256=sha(parent),testPath=v['testPath'],parentTestSha256=v['testSha256'],testSha256=sha(p),oldEightRetainedViaParentAndExactExtensionInverse=True,newDefinitions=2,connectedExpectedCases=19,additionalInput='literal1000000-byte maximum accepted; sender only sees clone, caller array unchanged, existing1000001 rejected test remains',independentBoundaryBasis='SS321 six destination table maximum1000000, Test literal not SUT maximum getter',additionalInputInsideExistingBeforePrice=True,originalBeforeEstimatePp=dict(low=.25,base=.65,high=1.3),capPp=2,formatIdempotent=True,MainChanged=False,productTestsExecuted=0,unchangedHelperTestHashes=v['unchangedHelperTestHashes'],files={q.name:sha(q) for q in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,old8Retained=True,newDefinitions=2,expectedTests=19,exactMaximumAcceptedInputAdded=True,manifestSha256=sha(O/'manifest.json'))))
