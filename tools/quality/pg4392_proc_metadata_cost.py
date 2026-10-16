"""Finite readonly /proc type micro-measurement. No Root proof, Unit/DB/permit action."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg4152_exact_failed_done_recover import durable, process

SLOT = 'pg4392-proc-metadata-cost-v1'

JAVA = r'''
import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

public final class ProcFilesystemCost {
  public interface Statfs { int call(MemorySegment path, MemorySegment state); }
  @FunctionalInterface interface Read { String type() throws Exception; }
  @SuppressWarnings("restricted")
  private static Statfs bind() {
    var linker = Linker.nativeLinker();
    var symbols = linker.defaultLookup();
    if (symbols.find("gnu_get_libc_version").isEmpty()) throw new IllegalStateException("glibc required");
    return MethodHandleProxies.asInterfaceInstance(Statfs.class,
        linker.downcallHandle(symbols.find("statfs").orElseThrow(),
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.ADDRESS, ValueLayout.ADDRESS)));
  }
  private static String fresh(Statfs call) throws Exception {
    try (var arena = Arena.ofConfined()) {
      var state = arena.allocate(120, 8);
      if (call.call(arena.allocateFrom("/proc"), state) != 0
          || state.get(ValueLayout.JAVA_LONG, 0) != 0x9fa0L)
        throw new IllegalStateException("fresh kernel type mismatch");
      return "proc";
    }
  }
  private static Map<String, Long> io() throws Exception {
    Map<String, Long> value = new LinkedHashMap<>();
    for (String line : Files.readString(Path.of("/proc/self/io")).split("\n")) {
      var parts = line.split(":", 2);
      if (parts.length == 2 && java.util.Set.of("rchar", "syscr", "read_bytes").contains(parts[0]))
        value.put(parts[0], Long.parseLong(parts[1].trim()));
    }
    if (value.size() != 3) throw new IllegalStateException("complete private self counters required");
    return value;
  }
  private static String measure(String phase, Read action) throws Exception {
    var bean = ManagementFactory.getThreadMXBean();
    if (!bean.isCurrentThreadCpuTimeSupported() || !bean.isThreadCpuTimeEnabled())
      throw new IllegalStateException("thread CPU counter unavailable");
    var before = io(); long cpu = bean.getCurrentThreadCpuTime(); long start = System.nanoTime();
    for (int i = 0; i < 200; i++)
      if (!action.type().equals("proc")) throw new IllegalStateException("independent type oracle mismatch");
    long wall = System.nanoTime() - start; cpu = bean.getCurrentThreadCpuTime() - cpu; var after = io();
    return "{\"phase\":\"" + phase + "\",\"calls\":200,\"nanos\":" + wall
        + ",\"threadCpuNanos\":" + cpu + ",\"rchar\":" + (after.get("rchar")-before.get("rchar"))
        + ",\"syscr\":" + (after.get("syscr")-before.get("syscr"))
        + ",\"physicalReadBytes\":" + (after.get("read_bytes")-before.get("read_bytes")) + "}";
  }
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !System.getProperty("os.name").equals("Linux")
        || !java.util.Set.of("amd64", "x86_64", "aarch64").contains(System.getProperty("os.arch")))
      throw new IllegalStateException("fixed Linux LP64 measurement only");
    var nativeCall = bind(); Read old = () -> Files.getFileStore(Path.of("/proc")).type();
    Read direct = () -> fresh(nativeCall);
    for (int i=0;i<20;i++) if (!old.type().equals("proc") || !direct.type().equals("proc"))
      throw new IllegalStateException("warmup type oracle mismatch");
    System.out.print("{\"actualExit\":0,\"sameKernelType\":true,\"measurementOnly\":true,\"authority\":false,\"samples\":[");
    for (int round=0;round<4;round++) {
      if (round>0) System.out.print(",");
      if (round%2==0) System.out.print(measure("jdkFileStore",old)+","+measure("freshStatfs",direct));
      else System.out.print(measure("freshStatfs",direct)+","+measure("jdkFileStore",old));
    }
    System.out.println("]}");
  }
}
'''


def payload():
    return 'JAVA=' + repr(JAVA) + '\nSLOT=' + repr(SLOT) + '\n' + r'''
from pathlib import Path
import hashlib,json,os,subprocess
assert os.geteuid()==0
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');before=manifest.read_bytes()
assert hashlib.sha256(before).hexdigest()=='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
assert json.loads(before)['source']['commit']=='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
for unit in ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:
 r=subprocess.run(['systemctl','show',unit,'--property=MainPID,ControlPID,Job'],capture_output=True,check=True)
 v=dict(line.split('=',1)for line in r.stdout.decode().splitlines());assert v=={'MainPID':'0','ControlPID':'0','Job':''}
os.umask(0o077);save=Path('/var/lib/pgpt-s1-preservation')/SLOT;save.mkdir(mode=0o700)
source=save/'ProcFilesystemCost.java'
with source.open('x')as f:f.write(JAVA);f.flush();os.fsync(f.fileno())
source.chmod(0o400)
with(save/'stdout.private.json').open('xb')as out,(save/'stderr.private.log').open('xb')as err:
 child=subprocess.Popen(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','--source','25',str(source)],stdout=out,stderr=err)
 p=Path('/proc')/str(child.pid);owner={'pid':child.pid,'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}
 (save/'owner.safe.json').write_text(json.dumps(owner));code=child.wait();out.flush();err.flush();os.fsync(out.fileno());os.fsync(err.fileno())
value={'actualExit':code,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','boot':'79a3260a-e16d-42bf-942a-b914ed144c28','javaSha256':hashlib.sha256(JAVA.encode()).hexdigest(),'operationsIssued':0,'formalAccepted':False}
assert manifest.read_bytes()==before
if code==0:value['result']=json.loads((save/'stdout.private.json').read_bytes())
(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
'''


def main():
    raw = payload(); compile(raw, '<fixed metadata cost read>', 'exec')
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    durable(out / 'start.safe.json', {'owner': process(os.getpid()), 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'replayAllowed': False})
    with management_gate(P / 'current-management-critical.lock'):
        with (out / 'stdout.private.log').open('xb') as stdout, (out / 'stderr.private.log').open('xb') as stderr:
            child = subprocess.Popen(SSH + ['sudo', '-n', 'python3', '-B', '-'], stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            durable(out / 'ssh.private.json', process(child.pid)); child.stdin.write(raw.encode()); child.stdin.close()
            code = child.wait(); stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    value = {'actualExit': code, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest()}
    if code == 0: value['result'] = json.loads((out / 'stdout.private.log').read_bytes())
    durable(out / 'manifest.safe.json', value); print(json.dumps(value))


if __name__ == '__main__':
    main()
