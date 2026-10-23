"""All125 source/110 additional physical owners; current API146, historical Batch261/Web51 byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7876_api_query_collection_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7880-api-query-collection-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1714_DbQueryDuration取得結線_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only role-aware trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7852-api-query-duration-trace-v3/manifest.json','1190a6b099334bcd2bd30c4cd199e27d97e00227b65efc64f2d1b51071843b28'),
      ('physical','PG7878-api-query-collection-six-post-v1/manifest.json',None),
      ('currentApi','PG7874-api-query-collection-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    physical=proofs['physical'];current=proofs['currentApi'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==123 and current['source']==physical['source']==compilation.SOURCE and current['tests']==146,
      'exact current role/source and all prior123')
    rows=[];spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'actual current/frozen/committed source')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all previous123 source bytes unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(Path(path).name in {'DbQueryDurationMetricCollector.java','DbQueryDurationMetricCollectorTest.java'}
              and path.startswith('src/schubert-nk-api/'),'only two declared new API files')
            row=dict(item,kind='TEST' if path.endswith('Test.java') else 'MAIN',rd='RD171/MON006,010..013',ui='252',ss='331,332,351',
              testIdFamily='DBCONN001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'every actual current API source input')
            row.update(qualificationRelationship='CURRENT_API_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_API_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentApi'],source=compilation.SOURCE,tests=146,suites=18))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=123,introduced=2));by_path={r['path']:r for r in rows};classes=[]
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
    require(len(rows)==125 and len(classes)==110 and len({r['className'] for r in classes})==110
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==30,'all125/110/currentAPI30, no historical execution transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentApiCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      unmeasuredProductionDependencyJarHashes=current['productionDependencyJarHashes'],
      historicalOriginalStepNotCurrentApiExecution=True,default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=125,physical=110,currentExecutable=30,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
