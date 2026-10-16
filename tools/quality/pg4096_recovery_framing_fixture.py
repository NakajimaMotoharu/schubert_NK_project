"""Run exact operational frame code in isolated stdin/pulse fixture; no M/A/DB/VM authority."""
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from pg1446_current_cold_stage import W

_source = Path(__file__).with_name('pg4088_failed_done_owned_sources.py').read_text()
_frames = [n.value for n in ast.parse(_source).body if isinstance(n, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id == 'FRAME' for t in n.targets)]
if len(_frames) != 1: raise ValueError('one exact operational framing body required')
FRAME = ast.literal_eval(_frames[0])


BODY = r'''
  private static void require(boolean v)throws IOException {if(!v)throw new IOException("fixture refusal");}
  @FunctionalInterface interface Work<T>{T run()throws Exception;}
  static void rejected(byte[] bytes,Work<Boolean> pulse)throws Exception {
    System.setIn(new ByteArrayInputStream(bytes));
    try{frame("fixture",pulse);throw new AssertionError("malformed/unknown control was accepted");}
    catch(IOException expected){require(expected.getMessage()!=null);}
  }
  public static void main(String[] args)throws Exception {
    var prior=System.in;var output=System.out;var sink=new ByteArrayOutputStream();
    try(var redacted=new PrintStream(sink,true,StandardCharsets.US_ASCII)) {
      System.setOut(redacted);
      System.setIn(new ByteArrayInputStream("CONTINUE\n".getBytes(StandardCharsets.US_ASCII)));
      frame("fixture",()->Boolean.TRUE);
      rejected("CONTINUE-extra\n".getBytes(StandardCharsets.US_ASCII),()->Boolean.TRUE);
      rejected(("x".repeat(33)+"\n").getBytes(StandardCharsets.US_ASCII),()->Boolean.TRUE);
      rejected(new byte[0],null);
      final int[] calls={0};
      rejected("CONTINUE".getBytes(StandardCharsets.US_ASCII),()->{calls[0]++;throw new IOException("pulse lost");});
      require(calls[0]==1);
      Thread.currentThread().interrupt();
      try{rejected("CONTINUE\n".getBytes(StandardCharsets.US_ASCII),()->Boolean.TRUE);}
      finally{Thread.interrupted();}
      try{rejected(new byte[0],()->{Thread.currentThread().interrupt();return Boolean.TRUE;});}
      finally{Thread.interrupted();}
      System.setIn(new ByteArrayInputStream("CONTINUE\n".getBytes(StandardCharsets.US_ASCII)) {
        @Override public synchronized int read(){int value=super.read();if(value==10)Thread.currentThread().interrupt();return value;}
      });
      try{frame("fixture",()->Boolean.TRUE);throw new AssertionError("interrupt while ACK read accepted");}
      catch(IOException expected){require(expected.getMessage()!=null);}
      finally{Thread.interrupted();}
    }finally{System.setIn(prior);System.setOut(output);}
    System.out.println("FRAMING_FIXTURE eight independent controls PASS noAuthority=true");
  }
}
'''


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'before', 'after', 'interrupt-v2'}: raise SystemExit('before, after or interrupt-v2; each new-only')
    os.umask(0o077); out = W / ('pg4096-recovery-framing-' + sys.argv[1] + '-v1'); out.mkdir()
    source = 'import java.io.*;import java.nio.charset.StandardCharsets;import java.util.Arrays;\npublic final class RecoveryFramingFixture {\n' + FRAME + BODY
    p = out / 'RecoveryFramingFixture.java'; p.write_text(source)
    jdk = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
    args = [str(jdk/'javac'), '-Xlint:all', '-Werror', '-d', str(out), str(p)]
    c = subprocess.run(args, capture_output=True, timeout=30); (out/'compile.log').write_bytes(c.stdout+c.stderr)
    value = {'compileExit': c.returncode, 'frameSha256': hashlib.sha256(FRAME.encode()).hexdigest(),
             'sourceSha256': hashlib.sha256(source.encode()).hexdigest(), 'productionPtAdded': 0, 'authorityIssued': False}
    if not c.returncode:
        args = [str(jdk/'java'), '-cp', str(out), 'RecoveryFramingFixture']
        r = subprocess.run(args, capture_output=True, timeout=10); (out/'result.log').write_bytes(r.stdout+r.stderr)
        value.update(actualExit=r.returncode, command=args)
    else: value['actualExit'] = c.returncode
    (out/'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return value['actualExit']


if __name__ == '__main__': raise SystemExit(main())
