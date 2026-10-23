"""All141 source/125 physical; current Web90 versus historical API174/Batch261."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg8058_http_duration_safe_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG8066-http-duration-safe-trace-v1'
PHYSICAL_WITNESS='PG8064-http-duration-safe-six-post-v1/manifest.json'
CURRENT_WEB_WITNESS='PG8062-http-duration-safe-post-v1/manifest.json'
SPEC='evidence/01_PT/018_NK-OPS-001/1725_HTTP極小MAX累積_追加品質単体テスト仕様書.md'
FAMILIES={'OverflowSafeHttpMeterRegistry':'HTTPDUR001..012','OverflowSafeDurationSupport':'HTTPDUR001..012'}
def require(value,message):
    if not value:raise ValueError(message)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only complete trace')
    proofs={};pins={}
    for key,path,digest in (
      ('previous','PG8042-exact-duration-trace-v5/manifest.json','232778568815d10f7fa3a952ab8e3210ab857a188858896f562fd51799a33a2e'),
      ('physical',PHYSICAL_WITNESS,None),
      ('currentWeb',CURRENT_WEB_WITNESS,None)):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['currentWeb'];p=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==138 and c['source']==p['source']==compilation.SOURCE and c['tests']==90 and c['suites']==11,'same-source current77 and previous129')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in p['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/frozen/current byte identity')
        if path in previous:
            row=copy.deepcopy(previous[path]);old_sha=row['sha256'];changed=old_sha!=item['sha256']
            if changed:
                require(Path(path).name in {'HttpMetricRecorder.java','HttpMetricRecorderTest.java','HttpMetricValveTest.java'},'only declared one Main and two fixture edits')
                row['specifications']=[*row.get('specifications',[]),spec]
            row.update(item,previousSourceByteSha256=old_sha,sourceChangedSincePreviousTrace=changed,sourceIntroducedSincePreviousTrace=False)
        else:
            name=Path(path).stem;program=name.removesuffix('Test')
            require(path.startswith('src/schubert-nk-web/') and program in FAMILIES
              and path=='src/schubert-nk-web/src/'+('test' if name.endswith('Test') else 'main')+'/java/dev/codex/schubert/nk/web/monitoring/'+name+'.java',
              'only declared registry/capability and independent tests')
            row=dict(item,kind='TEST' if name.endswith('Test') else 'MAIN',rd='RD171/MON003,005,010..013',ui='242,252',ss='324,332,351',
              testIdFamily=FAMILIES[program],specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in c['sourceFiles']:
            require(c['sourceFiles'][path]==item['sha256'],'every current Web input bound')
            row.update(qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentWeb'],source=compilation.SOURCE,tests=90,suites=11))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=3,unchanged=135,introduced=3));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('web','currentWeb'),('api','historicalApi'),('batch','historicalBatch')):
        proof=p[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'true physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'all physical owners present');executable=not entry.endswith('package-info.class') and entry not in {'dev/codex/schubert/nk/api/monitoring/ExactDurationSupport.class','dev/codex/schubert/nk/web/monitoring/OverflowSafeDurationSupport.class'}
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='web' and executable))
    require(len(rows)==141 and len(classes)==125 and len({r['className'] for r in classes})==125
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==20,'complete141/125/current20, no historical union')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentWebCounters=c['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      historicalOriginalStepNotCurrentWebExecution=True,default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=141,physical=125,currentExecutable=20,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

