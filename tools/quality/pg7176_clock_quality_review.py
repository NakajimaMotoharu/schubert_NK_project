"""Exact21 current raw dispositions and source/counter/domain proof, no target operation or PT replay."""
from collections import Counter
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7176-clock-quality-review-v1'
PINS={
 'current':('PG7168-observation-clock-post-v1/manifest.json','580abe8ff4eea75f6f2fda9fbd45c787f16b468a2536f16590705734f23bdcc5'),
 'oldRationale':('PG7086-registry-missing-post-v1/manifest.json','cb4c69760e6af1839fe1a8433445183f198ab7555005c9a979fc777cca30d353'),
 'physical':('PG7172-observation-clock-six-post-v1/manifest.json','7ee372ea833bd9ed3eecbda6f47e4c8b6713e1f6630d8e69f4e1f441928f91d4'),
 'trace':('PG7174-observation-clock-trace-v1/manifest.json','b0a847a40ca446eb3b77e018c46c7767063834a551596fceef7a97a392bf5d6c')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only review')
    witnesses={}
    for name,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'original public proof pin');witnesses[name]=json.loads(file.read_bytes())
    current=witnesses['current'];old=witnesses['oldRationale'];physical=witnesses['physical'];trace=witnesses['trace']
    require(current['source']==physical['source']==trace['source']=='3b2ef576cf46763d67a9e2914dc547afd2f93ef6'
      and current['tests']==91 and current['suites']==13 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual current91 and positive four counters')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items()),'all previous22 source bytes unchanged for14 rationale only')
    fresh=current['staticRaw']['pmd'];prior=old['staticRaw']['pmd']
    key=lambda row:json.dumps(row,sort_keys=True,separators=(',',':'))
    before=Counter(key(r) for r in prior['findings']);after=Counter(key(r) for r in fresh['findings'])
    require(before<=after and len(prior['findings'])==14 and len(fresh['findings'])==21
      and fresh['actualExit']==4 and fresh['processingErrors']==0,'all original14 actual rows and seven added rows')
    expected={('FilesystemHealthMonitor','observe','PRIVATE_LOCK'),('FilesystemHealthMonitor','observeNow','PRIVATE_LOCK'),
      ('MonitoringObservationClock','context','PRIVATE_LOCK'),
      *{('FilesystemHealthMonitor',method,kind) for method in ('observeNow','observeLocked') for kind in ('RuntimeException','Error')}}
    rows=[];seen=set()
    for text,count in (after-before).items():
        require(count==1,'one independent current raw row per classification');row=json.loads(text)
        if row['rule']=='AvoidSynchronizedStatement':kind='PRIVATE_LOCK'
        else:
            require(row['rule']=='AvoidCatchingGenericException','unknown rule is not classified automatically')
            kind='RuntimeException' if row['message']=='Avoid catching RuntimeException in try-catch block' else 'Error'
            require(row['message']==f'Avoid catching {kind} in try-catch block','exact unchecked type')
        identity=(row['class'],row['method'],kind)
        require(identity in expected and identity not in seen,'only exact seven reviewed tuples');seen.add(identity)
        rows.append(dict(raw=row,disposition='CONTRACT_REQUIRED',reasonDocument='018/1587',
                         testIds=['FSINPUT010','OBSCLOCK004','OBSCLOCK005','OBSCLOCK007','OBSCLOCK008']))
    require(seen==expected,'no dropped or unclassified finding')
    require(current['spotbugs']['findings']==0 and current['spotbugs']['actualExit']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],
      'real SB/CS zero')
    require(len(trace['sourceRows'])==39 and len(trace['physicalRows'])==33
      and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==22
      and physical['allPhysicalClassCount']==1702 and not physical['historicalWeb']['currentSourceExecutionAccepted'],
      'exact current22 distinct from historical Web, complete source/physical mapping')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,
      rawFindings=21,rawPmdExit=4,unchangedSourceRationaleCount=14,oldRationaleReference='018/1564,1569; never execution transfer',
      currentRows=rows,unclassified=0,suppressionsAdded=0,actualViolationsOutstanding=0,
      residualRisk='Actual Clock/FileStore ownership, finite polling/deadline/control/owned stop and runtime exporter remain HOLD',
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptExecutedByReview=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=21,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
