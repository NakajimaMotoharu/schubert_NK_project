"""Finite actual Java NativeIo read cost, not a synthetic live Root context or authorization."""
import inspect
import pg4392_proc_metadata_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4394-root-read-cost-v1'

JAVA = r'''
package dev.codex.schubert.nk.batch.platform;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public final class RootReadCost {
  @FunctionalInterface interface Read { byte[] read() throws Exception; }
  private static Map<String, Long> io() throws Exception {
    Map<String, Long> value = new HashMap<>();
    for (String line : Files.readString(Path.of("/proc/self/io")).split("\n")) {
      var parts = line.split(":", 2);
      if (parts.length == 2 && java.util.Set.of("rchar", "syscr", "read_bytes").contains(parts[0]))
        value.put(parts[0], Long.parseLong(parts[1].trim()));
    }
    if (value.size() != 3) throw new IllegalStateException("complete counters required");
    return value;
  }
  private static String measure(String phase, Read read) throws Exception {
    byte[] expected = read.read();
    for (int i=0;i<20;i++) if (!Arrays.equals(expected,read.read())) throw new IllegalStateException("read generation unstable");
    var bean = ManagementFactory.getThreadMXBean();
    if (!bean.isCurrentThreadCpuTimeSupported() || !bean.isThreadCpuTimeEnabled()) throw new IllegalStateException("CPU unsupported");
    var before=io();long cpu=bean.getCurrentThreadCpuTime();long began=System.nanoTime();
    for (int i=0;i<200;i++) if (!Arrays.equals(expected,read.read())) throw new IllegalStateException("read generation unstable");
    long nanos=System.nanoTime()-began;cpu=bean.getCurrentThreadCpuTime()-cpu;var after=io();
    return "{\"phase\":\""+phase+"\",\"calls\":200,\"nanos\":"+nanos+",\"threadCpuNanos\":"+cpu
        +",\"rchar\":"+(after.get("rchar")-before.get("rchar"))+",\"syscr\":"+(after.get("syscr")-before.get("syscr"))+"}";
  }
  public static void main(String[] args) throws Exception {
    if(args.length!=0)throw new IllegalArgumentException("no input");
    var io=new RootStartupContext.NativeIo();
    if(!io.procFilesystem().equals("proc"))throw new IllegalStateException("wrong kernel filesystem");
    System.out.println("{\"actualExit\":0,\"measurementOnly\":true,\"rootCaptureCalled\":false,\"authority\":false,\"samples\":["
        +measure("productionNativeIoUnitRead",()->io.unit(RootStartupContext.Service.MORNING))+","
        +measure("productionProcFilesystemRead",()->io.procFilesystem().getBytes(java.nio.charset.StandardCharsets.US_ASCII))+"]}");
  }
}
'''


def payload():
    raw = previous.payload()
    raw = once(raw, 'JAVA=' + repr(previous.JAVA), 'JAVA=' + repr(JAVA))
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    raw = once(raw, "source=save/'ProcFilesystemCost.java'", "source=save/'RootReadCost.java'")
    marker = "with(save/'stdout.private.json').open('xb')as out,(save/'stderr.private.log').open('xb')as err:"
    compile_step = """classes=save/'classes';classes.mkdir(mode=0o700)
release=manifest.parent
annotation=Path('/var/lib/pgpt-s1-preservation/pg4312-current-failed-owned-tools-v1/spotbugs-annotations-4.10.4.jar')
assert hashlib.sha256(annotation.read_bytes()).hexdigest()=='28fa4befaddce5d7b79b07c68e7c12fa27c5d9282c4229528717971606661ea3'
cp=str(release/'operations/batch.jar')+':'+str(release/'operations/lib/*')+':'+str(release/'api/lib/*')+':'+str(annotation)
with(save/'compile.private.log').open('xb')as log:
 result=subprocess.run(['/opt/jdk-25.0.4/bin/javac','--release','25','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(source)],stdout=log,stderr=log)
assert result.returncode==0
"""
    raw = once(raw, marker, compile_step + marker)
    old = "['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','--source','25',str(source)]"
    new = "['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',str(classes)+':'+cp,'dev.codex.schubert.nk.batch.platform.RootReadCost']"
    return once(raw, old, new)


def main():
    ns = {**vars(previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<actual NativeIo finite measurement>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
