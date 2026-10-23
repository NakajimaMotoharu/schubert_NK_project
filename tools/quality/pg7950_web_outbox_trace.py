"""All135 source/119 additional physical owners; current Web77, API162/Batch261 byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7942_web_outbox_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7950-web-outbox-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1721_WebOutbox観測経路_単体テスト仕様書.md'
FAMILIES={'WebOutboxMetricRecorder':'WEBOBXMET001..008','WebOutboxObservationRepository':'WEBOBXDB001..010','WebOutboxMetricCollector':'WEBOBXCONN001..008'}
def require(value,message):
    if not value:raise ValueError(message)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only complete trace')
    proofs={};pins={}
    for key,path,digest in (
      ('previous','PG7920-mq-event-trace-v1/manifest.json','014dded23795c0b234456d1952e0b55413d981d0904d75f20d39c3e0fc064735'),
      ('physical','PG7948-web-outbox-six-post-v1/manifest.json',None),
      ('currentWeb','PG7946-web-outbox-post-v1/manifest.json',None)):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['currentWeb'];p=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==129 and c['source']==p['source']==compilation.SOURCE and c['tests']==77 and c['suites']==10,'same-source current77 and previous129')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in p['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/frozen/current byte identity')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all previous129 source bytes unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            name=Path(path).stem;program=name.removesuffix('Test')
            require(path.startswith('src/schubert-nk-web/') and program in FAMILIES
              and path=='src/schubert-nk-web/src/'+('test' if name.endswith('Test') else 'main')+'/java/dev/codex/schubert/nk/web/monitoring/'+name+'.java',
              'only three declared Main and their independent tests')
            row=dict(item,kind='TEST' if name.endswith('Test') else 'MAIN',rd='RD171/MON003,005,010..013',ui='242,252',ss='324,332,351',
              testIdFamily=FAMILIES[program],specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in c['sourceFiles']:
            require(c['sourceFiles'][path]==item['sha256'],'every current Web input bound')
            row.update(qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentWeb'],source=compilation.SOURCE,tests=77,suites=10))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=129,introduced=6));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('web','currentWeb'),('api','historicalApi'),('batch','historicalBatch')):
        proof=p[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'true physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'all physical owners present');executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='web' and executable))
    require(len(rows)==135 and len(classes)==119 and len({r['className'] for r in classes})==119
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==18,'complete135/119/current18, no historical union')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentWebCounters=c['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      historicalOriginalStepNotCurrentWebExecution=True,default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=135,physical=119,currentExecutable=18,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
