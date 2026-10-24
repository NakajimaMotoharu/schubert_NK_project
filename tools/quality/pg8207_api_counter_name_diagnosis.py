"""BUG1691 own SDK TYPE-only diagnosis; no product PT rerun, service or business processing."""
import datetime
import json
import os
from pathlib import Path
import pg8178_web_prometheus_gauge_host as run
from host_tool_invocation import capture,verify

SLOT=run.host.W/'pg8207-counter-name-diagnosis-v1'
OUT=run.host.BASE/'PG8207-counter-name-diagnosis-v1'
RAW=run.host.BASE/'PG8206-api-prometheus-counter-host-v1/manifest.json'
RAW_SHA='e7ba3dd1435e89c39c55932c33574a9a33dbe99fb43373733485c596385e58f7'
HELPER=run.host.ROOT/'tools/quality/architecture/ApiCounterNameDiagnostic.java'


def main():
    invocation=capture(Path(__file__))
    run.require(not SLOT.exists() and not OUT.exists(),'new-only bounded diagnosis')
    run.require(run.host.sha(RAW)==RAW_SHA,'immutable failed original, not a successful case transfer')
    raw=json.loads(RAW.read_bytes())
    run.require(raw['actualExit']==1 and raw['source']==run.SOURCE and len(raw['cases'])==40,'original exact failed40 preserved')
    run.require(all(run.host.sha(Path(p))==h for p,h in raw['begin']['dependencyHashes'].items()),'same SDK/normal Main/JUnit dependencies')
    old_command=raw['stages'][1]['command']
    original_cp=old_command[old_command.index('-cp')+1]
    os.umask(0o077)
    SLOT.mkdir()
    classes=SLOT/'classes'
    classes.mkdir()
    for p in (classes/'prometheus.properties',SLOT/'empty-prometheus.properties'):
        with p.open('xb'):
            pass
    run.SLOT=SLOT
    cp=str(classes)+os.pathsep+original_cp
    jdk=run.host.TC/'jdk-25.0.4/bin'
    compile_row=run.step('diagnostic-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
             '-cp',cp,'-d',str(classes),str(HELPER)])
    run.require(compile_row['actualExit']==0,'own diagnostic compile0')
    row=run.step('diagnostic-run',[str(jdk/'java'),'-Dfile.encoding=UTF-8',
        '-Dprometheus.config='+str(SLOT/'empty-prometheus.properties'),'-cp',cp,
        'dev.codex.schubert.nk.api.monitoring.ApiCounterNameDiagnostic'])
    run.require(row['actualExit']==0,'bounded naming diagnosis actual terminal0')
    parsed={}
    for line in (SLOT/'diagnostic-run.log').read_text().splitlines():
        if '\t' in line:
            key,value=line.split('\t')
            run.require(key in {'EXISTING_TYPE','NO_UNIT_TYPE','SECONDS_NAME','PROCESSING_NAME'} and key not in parsed,
                        'only four public controlled metadata rows')
            parsed[key]=value
    run.require(set(parsed)=={'EXISTING_TYPE','NO_UNIT_TYPE','SECONDS_NAME','PROCESSING_NAME'},'all four actual metadata fields')
    run.require(parsed['NO_UNIT_TYPE']=='nk_mq_messages_total' and parsed['EXISTING_TYPE']!=parsed['NO_UNIT_TYPE'],
                'spec name unchanged; original supplied Producer unit metadata causes native mismatch')
    run.require(parsed['SECONDS_NAME']=='nk_db_query_duration_seconds'
                and parsed['PROCESSING_NAME']=='nk_mq_processing_duration_seconds','two seconds-suffix controls, not histogram Main PT')
    verify(invocation)
    value=dict(actualExit=0,source=raw['source'],originalFailureSha256=RAW_SHA,invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),observedMetadata=parsed,
        helperSha256=run.host.sha(HELPER),stages=[compile_row,row],scope='OWN_PUBLISHED_FIXED_TYPE_METADATA_ONLY',
        productTestsExecuted=0,diagnosisNotPtPass=True,actualVmActions=0,actualDatabaseActions=0,
        actualNetworkActions=0,actualServiceActions=0,newAccepted=0,formalUpdated=False)
    OUT.mkdir()
    run.host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,metadata=parsed,manifestSha256=run.host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
