"""Finite immutable-binding/validation cost only; no ownership or business operation."""
import inspect
import pg4394_root_read_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4396-binding-regex-cost-v1'
JAVA = r'''
package dev.codex.schubert.nk.batch.platform;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.LinuxFilesystemClassifier;
import java.lang.management.ManagementFactory;
import java.util.regex.Pattern;

public final class BindingRegexCost {
  @FunctionalInterface interface Work { Object run(); }
  private static volatile Object observed;
  private static String measure(String phase, int count, Work action) {
    for(int i=0;i<20;i++) observed=action.run();
    var bean=ManagementFactory.getThreadMXBean();
    if(!bean.isCurrentThreadCpuTimeSupported()||!bean.isThreadCpuTimeEnabled())throw new IllegalStateException("CPU unavailable");
    long cpu=bean.getCurrentThreadCpuTime(),start=System.nanoTime();
    for(int i=0;i<count;i++)observed=action.run();
    return "{\"phase\":\""+phase+"\",\"calls\":"+count+",\"nanos\":"+(System.nanoTime()-start)
      +",\"threadCpuNanos\":"+(bean.getCurrentThreadCpuTime()-cpu)+"}";
  }
  public static void main(String[] args) {
    if(args.length!=0||LinuxInodeSecurity.create().effectiveUid()!=0)throw new IllegalStateException("fixed root measurement");
    var pattern=Pattern.compile("/proc/self/fd/(0|[1-9][0-9]{0,9})");
    String held="/proc/self/fd/1234567";
    System.out.println("{\"actualExit\":0,\"measurementOnly\":true,\"authority\":false,\"samples\":["
      +measure("directoryBindings",200,LinuxDirectoryCalls::create)+","
      +measure("securityBindings",200,LinuxInodeSecurity::create)+","
      +measure("filesystemBindings",200,LinuxFilesystemClassifier::create)+","
      +measure("stringMatches",200000,()->held.matches("/proc/self/fd/(0|[1-9][0-9]{0,9})"))+","
      +measure("compiledPattern",200000,()->pattern.matcher(held).matches())+"]}");
  }
}
'''


def payload():
    raw = previous.payload()
    raw = once(raw, 'JAVA=' + repr(previous.JAVA), 'JAVA=' + repr(JAVA))
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    return raw.replace('RootReadCost', 'BindingRegexCost')


def main():
    ns = {**vars(previous.previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.previous.main), '<finite binding/validation measurement>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
