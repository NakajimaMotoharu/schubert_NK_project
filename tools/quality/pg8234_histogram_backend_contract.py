"""Bounded source and public SDK ABI read; javap never initializes target or runs product PT."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
SLOT=host.W/'pg8234-histogram-backend-contract-v1'
OUT=host.BASE/'PG8234-histogram-backend-contract-v1'
SDK=host.BASE/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
SDK_SHA='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'
SDK_POST=host.BASE/'PG8173-prometheus-sdk-exact-source-post-v1/manifest.json'
SDK_POST_SHA='a5a2bfbe93bf8b8cc9521b67d1ce4a4c540bc967d7814927b0417807c6b30572'
SOURCES=[
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/'+n+'.java' for n in
 ('ExactDurationMeterRegistry','ExactDurationSupport','DbQueryDurationMetricRecorder','MqProcessingDurationMetricRecorder')]
SOURCES+=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/'+n+'.java' for n in
 ('OverflowSafeHttpMeterRegistry','OverflowSafeDurationSupport','HttpMetricRecorder')]
SOURCES+=['src/schubert-nk-'+role+'/pom.xml' for role in ('bootstrap','api','web')]
TARGETS=(
 'io.micrometer.prometheusmetrics.PrometheusMeterRegistry',
 'io.prometheus.metrics.model.registry.MultiCollector',
 'io.prometheus.metrics.model.registry.PrometheusRegistry',
 'io.prometheus.metrics.model.snapshots.HistogramSnapshot',
 'io.prometheus.metrics.model.snapshots.HistogramSnapshot$Builder',
 'io.prometheus.metrics.model.snapshots.HistogramSnapshot$HistogramDataPointSnapshot',
 'io.prometheus.metrics.model.snapshots.HistogramSnapshot$HistogramDataPointSnapshot$Builder',
 'io.prometheus.metrics.model.snapshots.ClassicHistogramBuckets',
 'io.prometheus.metrics.model.snapshots.ClassicHistogramBuckets$Builder',
 'io.prometheus.metrics.model.snapshots.MetricMetadata',
 'io.prometheus.metrics.model.snapshots.MetricSnapshots',
 'io.prometheus.metrics.model.snapshots.Labels',
 'io.prometheus.metrics.model.snapshots.Unit',
 'io.prometheus.metrics.tracer.common.SpanContext',
 'io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter',
 'io.micrometer.core.instrument.distribution.CountAtBucket',
 'io.micrometer.core.instrument.distribution.HistogramSnapshot',
 'io.micrometer.core.instrument.simple.SimpleMeterRegistry')


def require(value,message):
    if not value:
        raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only metadata read job')
    require(host.sha(SDK)==SDK_SHA and host.sha(SDK_POST)==SDK_POST_SHA,'prepared public SDK and independent full-source qualification')
    sdk=json.loads(SDK.read_bytes())
    jars={r['jar']['path']:r['jar']['sha256'] for r in sdk['downloaded'].values()}
    jars.update({r['path']:r['sha256'] for r in sdk['reused'].values()})
    require(len(jars)==15 and all(host.sha(Path(p))==h for p,h in jars.items()),'all15 fixed SDK bytes')
    hashes={}
    for path in SOURCES:
        old=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        hashes[path]=hashlib.sha256(old).hexdigest()
        require(host.sha(host.ROOT/path)==hashes[path],'all selected current source/pom equal fixed candidate')
    os.umask(0o077)
    SLOT.mkdir()
    env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8')
    cp=os.pathsep.join(jars)
    rows=[]
    for n,name in enumerate(TARGETS,1):
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-protected','-classpath',cp,name]
        stem=f'abi-{n:02d}'
        host.write(SLOT/(stem+'-begin.safe.json'),dict(command=command,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        with (SLOT/(stem+'.stdout.log')).open('xb') as out,(SLOT/(stem+'.stderr.log')).open('xb') as err:
            child=subprocess.Popen(command,cwd=SLOT,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True)
            host.write(SLOT/(stem+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=command,cwd=str(SLOT)))
            code=child.wait(timeout=30)
            for f in (out,err):
                f.flush()
                os.fsync(f.fileno())
        row=dict(className=name,command=command,actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 stdoutSha256=host.sha(SLOT/(stem+'.stdout.log')),stderrSha256=host.sha(SLOT/(stem+'.stderr.log')),
                 targetInitialized=False)
        host.write(SLOT/(stem+'-exit.safe.json'),row)
        require(code==0,'read exact public vendor ABI only, unknown class is not a supported API')
        rows.append(row)
    require(all(host.sha(Path(p))==h for p,h in jars.items())
            and all(host.sha(host.ROOT/p)==h for p,h in hashes.items()),'fixed source and SDK after metadata read')
    verify(invocation)
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sourceHashes=hashes,sdkManifestSha256=SDK_SHA,sdkPostSha256=SDK_POST_SHA,sdkJarHashes=jars,abi=rows,
        targetLoadedOrInitialized=False,productTestsExecuted=0,ordinaryRegistryInitialized=False,
        actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,
        metadataOnlyNotPtPass=True,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sourceFiles=len(hashes),publicSdkTypes=len(rows),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
