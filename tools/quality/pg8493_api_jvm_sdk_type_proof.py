"""Independent fixed SDK class-loader names/types proof; no binder or application execution."""
import datetime
import json
from pathlib import Path
import scoped_prometheus_post as post
from host_tool_invocation import capture, verify

host = post.host
SLOT = host.W / 'pg8493-api-jvm-sdk-type-proof-v1'
OUT = host.BASE / 'PG8493-api-jvm-sdk-type-proof-v1'
JAR = host.TC / 'm2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
SHA = '9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists() and host.sha(JAR) == SHA
    SLOT.mkdir()
    post.SLOT = SLOT
    texts, receipts = {}, {}
    for name, qualified in (
        ('class-loader', 'io.micrometer.core.instrument.binder.jvm.ClassLoaderMetrics'),
        ('conventions', 'io.micrometer.core.instrument.binder.jvm.convention.micrometer.MicrometerJvmClassLoadingMeterConventions'),
        ('uptime', 'io.micrometer.core.instrument.binder.system.UptimeMetrics')):
        row, text = post.step(name, [str(host.TC / 'jdk-25.0.4/bin/javap'), '-c', '-p', '-classpath', str(JAR), qualified])
        assert row['actualExit'] == 0 and not row['timedOut']
        texts[name], receipts[name] = text, row
    mapping = (
        ('currentClassCountConvention', 'jvm.classes.loaded', 'Gauge'),
        ('unloadedConvention', 'jvm.classes.unloaded', 'FunctionCounter'),
        ('loadedConvention', 'jvm.classes.loaded.count', 'FunctionCounter'))
    loader = texts['class-loader']
    points = [loader.index('JvmClassLoadingMeterConventions.' + m[0]) for m in mapping] + [len(loader)]
    assert points == sorted(points)
    for i, (method, name, kind) in enumerate(mapping):
        body = texts['conventions'].split(' ' + method + '();\n', 1)[1].split('\n  public ', 1)[0]
        assert '// String ' + name + '\n' in body
        part = loader[points[i]:points[i + 1]]
        assert 'InterfaceMethod io/micrometer/core/instrument/' + kind + '.builder:' in part
        if kind == 'Gauge':
            assert 'FunctionCounter.builder' not in part
    uptime = texts['uptime']
    assert 'String process.uptime' in uptime and 'String process.start.time' in uptime and uptime.count('InterfaceMethod io/micrometer/core/instrument/TimeGauge.builder:') == 2 and 'TimeUnit.MILLISECONDS' in uptime
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), source='fe91dc6898c2f5b679c8fe14c70a490bed770c73', sdkJarSha256=SHA, mapping=[dict(method=m,name=n,kind=k) for m,n,k in mapping], uptimeKind='TimeGauge', uptimeBase='MILLISECONDS', receipts=receipts, invocation=invocation, bug='BUG-1705', rollout='YKT-1456', metadataOnly=True, sdkBinderInvoked=False, productTestsExecuted=0, coverageQualified=False, whole451Accepted=False, formalUpdated=False, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, mappings=len(mapping), appExecuted=False, manifestSha256=host.sha(OUT / 'manifest.json'))))

