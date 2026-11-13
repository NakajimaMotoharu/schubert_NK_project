from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';root=R/'src/schubert-nk-web/src';t=root/'test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeHealthTest.java';old=t.read_text();assert len(re.findall(r'@Test\b',old))==4
new='''
  @Test
  void health005ManagementReadyRequiresCapturedObjectAndPropagatesProbeFailure() {
    var calls = new ArrayList<String>();
    var captured = new Object();
    assertFalse(WebRuntimeHealth.ready(null, value -> {
      throw new AssertionError("absent management must not be probed");
    }));
    assertFalse(WebRuntimeHealth.ready(captured, value -> {
      assertSame(captured, value);
      calls.add("not-ready");
      return false;
    }));
    assertTrue(WebRuntimeHealth.ready(captured, value -> {
      assertSame(captured, value);
      calls.add("ready");
      return true;
    }));
    var primary = new LinkageError("synthetic management failure");
    assertSame(primary, assertThrows(LinkageError.class,
        () -> WebRuntimeHealth.ready(captured, value -> {
          assertSame(captured, value);
          calls.add("failed");
          throw primary;
        })));
    assertEquals(List.of("not-ready", "ready", "failed"), calls);
  }
'''
assert old.endswith('}\n');t.write_text(old[:-2]+new+'}\n');f=root/'test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeFailureSignalTest.java';assert not f.exists();f.write_text('''package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** SS313342352 / PT-OPS-WEB-REM002: the captured terminal flag, no resource operation. */
final class WebRuntimeFailureSignalTest {
  @Test
  void signal001BothCallbacksMarkOnlyCapturedFlagAndRemainIdempotent() {
    assertThrows(NullPointerException.class, () -> new WebRuntimeFailureSignal<>(null));
    var captured = new AtomicBoolean();
    var unrelated = new AtomicBoolean();
    var signal = new WebRuntimeFailureSignal<IllegalStateException>(captured);
    assertFalse(captured.get());
    signal.run();
    assertTrue(captured.get());
    signal.run();
    assertTrue(captured.get());
    assertFalse(unrelated.get());
    captured.set(false);
    signal.accept(new IllegalStateException("synthetic ignored callback"));
    assertTrue(captured.get());
    signal.accept(new IllegalStateException("second ignored callback"));
    assertTrue(captured.get());
    assertFalse(unrelated.get());
  }
}
''')
subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'-i',str(t),str(f)],check=True);newbody=t.read_text();idx=newbody.index('  @Test\n  void health005');assert newbody[:idx].rstrip()+'\n}\n'==old.rstrip()+'\n'
source='a769422d3bdb936daadccc974ccecbe7c32b3086';main=[root/'main/java/dev/codex/schubert/nk/web/bootstrap'/n for n in ['WebRuntimeHealth.java','WebRuntimeFailureSignal.java']];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in main:assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(p.relative_to(R))])).hexdigest()
O=B/'evidence/PG29020-health-signal-whole6-source-closure-v1';assert not O.exists();O.mkdir();(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=source,MainChanged=False,originalWhole4InverseExact=True,oldWhole4Sha256=hashlib.sha256(old.encode()).hexdigest(),mainInputHashes={str(p.relative_to(R)):sha(p) for p in main},testInputHashes={str(p.relative_to(R)):sha(p) for p in [t,f]},wholeTestCount=6,newDefinitions=2,independentOracle='Existing4 retain literal ordered shortcircuit/provider identity. Newmanagement null no probe; same captured object false/true and Error identity; literal ordered not-ready/ready/failed list. Signal constructor null rejection, both callbacks make only captured AtomicBoolean true and repeated callbacks harmless. No expected from Production.',wholeSourcesAndTestsReviewed=True,jdkOnly=True,actualHttpRootDbJmsThreadNativeActions=0,productTestsExecuted=0,newAcceptance=0),ensure_ascii=False,indent=2)+'\n')
print('Main2 unchanged; whole4 inverse exact; new2 meaningful pure normal tests; ProductPT0')
