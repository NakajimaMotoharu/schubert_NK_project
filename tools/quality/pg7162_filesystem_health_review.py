"""All15 static rows/reused byte-identical rationale and exact standard disk getter meaning."""
from collections import Counter
import json
import os
import subprocess
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7162-filesystem-health-review-v1'
SLOT=host.W/'pg7162-filesystem-health-review-v1'
PINS={
 'current':('PG7154-filesystem-health-post-v1/manifest.json','a86ed6ca91bc6df6d9bd886cf7b487a5253176a2f22b55c7b82b31657a5e110f'),
 'oldApplicability':('PG7086-registry-missing-post-v1/manifest.json','cb4c69760e6af1839fe1a8433445183f198ab7555005c9a979fc777cca30d353'),
 'physical':('PG7158-filesystem-health-six-post-v1/manifest.json','69b2ab7cb63e296a9851c3dd0d34daca4c71b77f841384dc350f1258721dd3a6'),
 'trace':('PG7160-filesystem-health-trace-v1/manifest.json','2d22a8b9269ed8fc3e62df273cdb087914a1a5980386622a5674e4719e6ddb8c')}
CORE=host.TC/'m2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
CORE_SHA='9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists() and not SLOT.exists(),'new-only review/source-only SDK parse')
    witnesses={}
    for name,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact public original witness pin');witnesses[name]=json.loads(file.read_bytes())
    current=witnesses['current'];old=witnesses['oldApplicability'];physical=witnesses['physical'];trace=witnesses['trace']
    require(current['source']==physical['source']==trace['source']=='bbc230f8a892d3ad2e47aeaccbe37bbb86bd97b6'
      and current['tests']==83 and current['suites']==12 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current83 and all positive four counters')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items()),
            'all old22 Java source bytes unchanged, only static rationale inherited, never old PT execution')
    fresh=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    canonical=lambda row:json.dumps(row,sort_keys=True,separators=(',',':'))
    remainder=Counter(canonical(r) for r in fresh['findings'])-Counter(canonical(r) for r in before['findings'])
    require(len(fresh['findings'])==15 and len(before['findings'])==14 and fresh['actualExit']==4 and fresh['processingErrors']==0
      and sum(remainder.values())==1 and Counter(canonical(r) for r in before['findings'])<=Counter(canonical(r) for r in fresh['findings']),
      'all14 prior raw findings preserved with one and only one new row')
    row=json.loads(next(iter(remainder)))
    require(row['class']=='FilesystemHealthMonitor' and row['method']=='observe' and row['rule']=='AvoidSynchronizedStatement',
            'unknown findings are not auto-disposed')
    require(not current['staticRaw']['checkstyle']['findings'] and current['staticRaw']['checkstyle']['actualExit']==0
      and current['spotbugs']['findings']==0 and current['spotbugs']['actualExit']==0,'actual CS/SB zero')
    require(len(trace['sourceRows'])==37 and len(trace['physicalRows'])==32
      and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==21
      and physical['allPhysicalClassCount']==1701 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'current21 independent from historical Web10, all source/physical ownership')
    require(host.sha(CORE)==CORE_SHA,'existing exact official core byte, not a new runtime dependency')
    command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-classpath',str(CORE),'-v',
             'io.micrometer.core.instrument.binder.system.DiskSpaceMetrics']
    os.umask(0o077);SLOT.mkdir()
    raw=subprocess.run(command,capture_output=True,check=False)
    with (SLOT/'sdk-definition.safe.log').open('xb') as stream:stream.write(raw.stdout)
    text=raw.stdout.decode('utf-8')
    require(raw.returncode==0 and 'java/io/File.getUsableSpace:()J' in text
      and 'java/io/File.getTotalSpace:()J' in text and host.sha(CORE)==CORE_SHA,'standard SDK getter definition parse, no class load/init')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,
      rawFindings=15,rawPmdExit=4,oldByteIdenticalRationaleCount=14,oldRationaleReference='018/1564,1569; not execution transfer',
      newRow=dict(raw=row,disposition='CONTRACT_REQUIRED',reasonDocument='018/1583',testIds=['FSINPUT007','FSINPUT010']),
      unclassified=0,suppressionsAdded=0,actualViolationsOutstanding=0,
      sdkDefinition=dict(command=command,actualExit=raw.returncode,coreSha256=CORE_SHA,stdoutSha256=host.sha(SLOT/'sdk-definition.safe.log'),
        methodReferences=['File.getUsableSpace','File.getTotalSpace'],classLoadOrInitialization=False,executedByBatchPt=False),
      residualRisk='Actual FileStore boundedness, validated production root, poll deadline and owned stop remain unaccepted/HOLD',
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptExecutedByReview=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=15,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
