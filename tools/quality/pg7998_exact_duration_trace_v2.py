"""All137 source/121 additional physical owners; API174 vs historical Batch261/Web77 byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7994_exact_duration_six_compile_v2 as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7998-exact-duration-trace-v2'
SPEC='evidence/01_PT/018_NK-OPS-001/1723_Duration極小MAX混在_追加品質単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only role-aware trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7950-web-outbox-trace-v1/manifest.json','f27a24b8e1c2d9f72519f64f85f97a8baf80ffae4c0824fffd71d964a3043800'),
      ('physical','PG7996-exact-duration-six-post-v2/manifest.json',None),
      ('currentApi','PG7992-exact-duration-post-v2/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    physical=proofs['physical'];current=proofs['currentApi'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==135 and current['source']==physical['source']==compilation.SOURCE and current['tests']==174,
      'exact current role/source and all prior135')
    rows=[];spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'actual current/frozen/committed source')
        if path in previous:
            row=copy.deepcopy(previous[path]);old_sha=row['sha256'];changed=old_sha!=item['sha256']
            if changed:
                require(Path(path).name in {'DbQueryDurationMetricRecorder.java','MqProcessingDurationMetricRecorder.java','DbQueryDurationMetricRecorderTest.java','MqProcessingDurationMetricRecorderTest.java','DbQueryDurationMetricCollectorTest.java'},'only declared five duration implementation/fixture edits')
                row['specifications']=[*row.get('specifications',[]),spec]
            row.update(item,previousSourceByteSha256=old_sha,sourceChangedSincePreviousTrace=changed,sourceIntroducedSincePreviousTrace=False)
        else:
            require(Path(path).name in {'ExactDurationMeterRegistry.java','ExactDurationMeterRegistryTest.java'}
              and path.startswith('src/schubert-nk-api/'),'only two declared new API files')
            row=dict(item,kind='TEST' if path.endswith('Test.java') else 'MAIN',rd='RD171/MON005,006,010..013',ui='252',ss='321,323,351',
              testIdFamily='EXDUR001..010',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'every actual current API source input')
            row.update(qualificationRelationship='CURRENT_API_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_API_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentApi'],source=compilation.SOURCE,tests=174,suites=21))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        rows.append(row)
    counts=anchors(rows,previous,dict(changed=5,unchanged=130,introduced=2));by_path={r['path']:r for r in rows};classes=[]
    for role,key in (('api','currentApi'),('batch','historicalBatch'),('web','historicalWeb')):
        domain=physical[key]
        for name,digest in domain['physicalClasses'].items():
            actual_role,entry=name.split(':',1);require(role==actual_role,'true physical role, no namespace alias')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in by_path,'all physical nested/metadata owners')
            executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=by_path[path]['owner'],
              qualificationDomain='CURRENT_API_QUALIFIED' if role=='api' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=domain['source'],executable=executable,currentSourceExecutionAccepted=role=='api' and executable))
    require(len(rows)==137 and len(classes)==121 and len({r['className'] for r in classes})==121
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==36,'all137/121/currentAPI36, no historical execution transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentApiCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      unmeasuredProductionDependencyJarHashes=current['productionDependencyJarHashes'],
      historicalOriginalStepNotCurrentApiExecution=True,default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=137,physical=121,currentExecutable=36,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()

