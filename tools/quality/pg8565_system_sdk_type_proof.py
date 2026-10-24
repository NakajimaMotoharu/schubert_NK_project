"""Fixed public SDK CPU/FD name-type-unit metadata, no SDK/application execution."""
import datetime
import json
from pathlib import Path
import scoped_prometheus_post as post
from host_tool_invocation import capture, verify

host = post.host
SLOT = host.W / 'pg8565-system-sdk-type-proof-v1'
OUT = host.BASE / 'PG8565-system-sdk-type-proof-v1'
JAR = host.TC / 'm2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
SHA = '9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists() and host.sha(JAR) == SHA
    SLOT.mkdir()
    post.SLOT = SLOT
    texts, receipts = {}, {}
    for name, qualified in (
        ('cpu', 'io.micrometer.core.instrument.binder.system.ProcessorMetrics'),
        ('conventions', 'io.micrometer.core.instrument.binder.jvm.convention.micrometer.MicrometerJvmCpuMeterConventions'),
        ('fd', 'io.micrometer.core.instrument.binder.system.FileDescriptorMetrics')):
        row, text = post.step(name, [str(host.TC / 'jdk-25.0.4/bin/javap'), '-c', '-p', '-classpath', str(JAR), qualified])
        assert row['actualExit'] == 0 and not row['timedOut']
        texts[name], receipts[name] = text, row
    mapping = [('cpuCountConvention', 'system.cpu.count', 'Gauge'), ('processCpuLoadConvention', 'process.cpu.usage', 'Gauge'), ('cpuTimeConvention', 'process.cpu.time', 'FunctionCounter')]
    cpu = texts['cpu']
    starts = [cpu.index('JvmCpuMeterConventions.' + method) for method, _, _ in mapping]
    assert starts == sorted(starts)
    for i, (method, name, kind) in enumerate(mapping):
        body = texts['conventions'].split(' ' + method + '();\n', 1)[1].split('\n  public ', 1)[0]
        assert '// String ' + name + '\n' in body
        part = cpu[starts[i]:starts[i + 1] if i + 1 < len(starts) else cpu.index('  private double invoke')]
        assert 'InterfaceMethod io/micrometer/core/instrument/' + kind + '.builder:' in part
    assert 'String ns\n' in cpu and 'FunctionCounter$Builder.baseUnit:' in cpu
    fd = texts['fd']
    for name, getter in [('process.files.open', 'getOpenFileDescriptorCount'), ('process.files.max', 'getMaxFileDescriptorCount')]:
        assert 'String ' + name + '\n' in fd and 'String ' + getter + '\n' in fd
    assert fd.count('InterfaceMethod io/micrometer/core/instrument/Gauge.builder:') == 2
    assert all('java.lang.AutoCloseable' not in text.split('\n', 3)[1] for key, text in texts.items() if key != 'conventions')
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), sdkJarSha256=SHA, mapping=[dict(method=m, name=n, kind=k) for m, n, k in mapping], fdNames=['process.files.open', 'process.files.max'], fdKind='Gauge', cpuTimeUnit='ns', receipts=receipts, invocation=invocation, metadataOnly=True, sdkBinderInvoked=False, productTestsExecuted=0, coverageQualified=False, whole451Accepted=False, formalUpdated=False, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, mappings=len(mapping) + 2, appExecuted=False, manifestSha256=host.sha(OUT / 'manifest.json'))))
