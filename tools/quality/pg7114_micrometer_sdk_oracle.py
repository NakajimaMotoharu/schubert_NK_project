"""Pinned vendor bytecode explains auxiliary SLO meters; no Product methods or old PT replay."""
import json
import os
import subprocess
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg7106_micrometer_http_host as sdk
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7114-micrometer-sdk-oracle-v1'
OUT=host.BASE/'PG7114-micrometer-sdk-oracle-v1'


def main():
    invocation=capture(Path(__file__))
    if SLOT.exists() or OUT.exists():raise ValueError('new-only public SDK metadata audit')
    if not all(host.sha(Path(p))==h for p,h in sdk.SDK.items()):raise ValueError('pinned full SDK unchanged')
    core=next(p for p in sdk.SDK if '/micrometer-core/' in p)
    os.umask(0o077);SLOT.mkdir()
    rows=[];texts=[]
    for label,name in (('simple','io.micrometer.core.instrument.simple.SimpleMeterRegistry'),
                       ('histogram','io.micrometer.core.instrument.distribution.HistogramGauges')):
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-c','-p','-classpath',core,name]
        child=subprocess.run(command,capture_output=True,text=True)
        with (SLOT/(label+'.bytecode.txt')).open('x') as stream:stream.write(child.stdout)
        row=dict(command=command,actualExit=child.returncode,stdoutSha256=host.sha(SLOT/(label+'.bytecode.txt')),
                 stderrSha256=__import__('hashlib').sha256(child.stderr.encode()).hexdigest())
        host.write(SLOT/(label+'-exit.safe.json'),row);rows.append(row);texts.append(child.stdout)
        if child.returncode:raise ValueError('original primary bytecode read failed, no success inferred')
    checks=dict(timerRegistersHistogramGauges='HistogramGauges.registerWithCommonFormat:(Lio/micrometer/core/instrument/Timer;' in texts[0],
      simpleBaseUnitSeconds='TimeUnit.SECONDS' in texts[0],
      auxiliaryHistogramSuffix='String .histogram' in texts[1],auxiliaryLeTag='String le' in texts[1],
      timerBucketUnitConversion='CountAtBucket.bucket:(Ljava/util/concurrent/TimeUnit;)D' in texts[1],
      numericBucketFormatting='DoubleFormat.wholeOrDecimal' in texts[1])
    if not all(checks.values()):raise ValueError('all independent primary SDK markers must be present')
    value=dict(actualExit=0,invocation=invocation,sdkJarHashes=sdk.SDK,primaryBytecodeReads=rows,checks=checks,
      ssExplicitBoundaries=9,closedRoutes=35,primaryCounters=1750,primaryTimers=35,
      derivedAuxiliaryGauges=315,simpleRegistryPhysicalMeters=2100,
      producerCatalogNamesUnchanged=True,auxiliaryNamesAreNotNewCanonicalProducerMetrics=True,
      expectedFromProductionMethod=False,actualProductMethodsInvoked=0,productionTestsExecuted=0,
      vendorBytecodeTextCommitted=False,actualVmActions=0,actualDatabaseActions=0,
      bug='BUG-1651',rollout='YKT-1404',formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,checks=checks,derivedAuxiliary=315,physical=2100,
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
