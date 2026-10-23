"""All65 source/57 physical owners; only currentAPI3 executed, historical domains never transferred."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors

SOURCE='72b65394206ac449604e4cffc5d703c55d8fc2f7'
OUT=host.BASE/'PG7308-api-async-metric-trace-v1'
SOURCE_COUNT=65
PREVIOUS_COUNT=61
CURRENT_TESTS=8
CURRENT_SUITES=1
CURRENT_EXECUTABLE=3
ADDED_PHYSICAL=57
SPEC_ID=1623
RESULT_ID=1624
PHYSICAL_DOC_ID=1625
PINS={
 'currentApi':('PG7302-api-async-metric-post-v1/manifest.json','246b450c115954b30a6246c71bda7e5a2b25273fea211e32d729eb9b1b0304fa'),
 'physical':('PG7306-api-async-metric-six-post-v1/manifest.json','4d112f8dd1a30644becce423abeeabde2df9d65811736ee08de831f9b9b7491c'),
 'previous':('PG7294-transfer-health-trace-v1/manifest.json','422900508bcbdabcdf26f69a357bb93456b3cc44fdd76301662f7277198b33be')}
DOCS={1623:'1623_APIAsyncJobMetric_単体テスト仕様書.md',1624:'1624_APIAsyncJobMetric_実行結果.md',
      1625:'1625_APIAsyncJobMetric_実Jar・資格domain.md'}
ALLOWED_NEW={'AsyncJobMetricRecorder.java','AsyncJobMetricRecorderTest.java','package-info.java','pom.xml'}
TEST_ID_FAMILY='ASYNCGAUGE001..008'
EDITED_EXISTING=set()
NEW_SOURCE_CONTRACTS={}
ADDITIONAL_SPEC_IDS_BY_PATH={}

def require(value,message):
    if not value:raise ValueError(message)

def refs(*numbers):
    result=[]
    for number in numbers:
        path=host.ROOT/'evidence/01_PT/018_NK-OPS-001'/DOCS[number]
        require(path.is_file(),'exact declared current document')
        result.append(dict(path=str(path.relative_to(host.ROOT)),sha256=host.sha(path)))
    return result

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only exact multidomain trace')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public witness');proofs[key]=json.loads(file.read_bytes())
    current=proofs['currentApi'];physical=proofs['physical'];previous=proofs['previous']
    require(current['source']==physical['source']==SOURCE and current['tests']==CURRENT_TESTS
      and current['actualCrcMismatch']==0 and current['actualSessions']==1,'actual current API original qualification')
    prior={row['path']:row for row in previous['sourceRows']};require(len(prior)==PREVIOUS_COUNT,'all unique previous source rows')
    rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        require(host.sha(host.ROOT/path)==item['sha256']==hashlib.sha256(blob).hexdigest(),'current path/committed byte/normal compile source exact')
        if path in prior:
            row=dict(prior[path]);changed=row['sha256']!=item['sha256']
            require(changed is (path in EDITED_EXISTING),'only explicitly declared existing source edits')
            row.update(sha256=item['sha256'],previousSourceByteSha256=prior[path]['sha256'],sourceChangedSincePreviousTrace=changed,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path.startswith('src/schubert-nk-api/') and Path(path).name in ALLOWED_NEW,'only declared four newly tracked API files')
            family,spec=NEW_SOURCE_CONTRACTS.get(Path(path).name,(TEST_ID_FAMILY,SPEC_ID))
            row=dict(item,kind='DEPENDENCY_DESCRIPTOR' if path.endswith('/pom.xml') else 'TEST' if path.endswith('Test.java') else 'MAIN',
              rd='MON005..013',ui='252',ss='324,331,351',testIdFamily=family,specifications=refs(spec),
              previousSourceByteSha256=None,sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',results=refs(PHYSICAL_DOC_ID),
              compileWitness=dict(path=PINS['physical'][0],sha256=PINS['physical'][1],source=SOURCE),
              componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',currentSourceCoverageTransferred=False)
        elif path.startswith('src/schubert-nk-api/') and '/monitoring/' in path:
            require(current['sourceFiles'].get(path)==item['sha256'],'every current API Main/Test/metadata actually executed/compiled snapshot input')
            row.update(qualificationRelationship='CURRENT_API_EXECUTION_OR_DECLARED_METADATA',results=refs(RESULT_ID,PHYSICAL_DOC_ID),
              executionWitness=dict(path=PINS['currentApi'][0],sha256=PINS['currentApi'][1],source=SOURCE,tests=CURRENT_TESTS,suites=CURRENT_SUITES),
              componentCounterScope='ALL_CURRENT_API_EXECUTABLES_ONLY',currentSourceCoverageTransferred=False)
        else:
            if 'results' in row:row['historicalResults']=row.pop('results')
            row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',
              componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS',currentSourceCoverageTransferred=False)
        if path in ADDITIONAL_SPEC_IDS_BY_PATH:
            row['additionalSpecifications']=refs(*ADDITIONAL_SPEC_IDS_BY_PATH[path])
            row['additionalTestIdFamily']='GENMET001..008'
        rows.append(row)
    counts=anchors(rows,prior,dict(changed=len(EDITED_EXISTING),unchanged=PREVIOUS_COUNT-len(EDITED_EXISTING),introduced=SOURCE_COUNT-PREVIOUS_COUNT))
    by_path={row['path']:row for row in rows};classes=[]
    for label,domain in (('CURRENT_API_QUALIFIED',physical['currentApi']),
                        ('HISTORICAL_BATCH_BYTE_IDENTITY_ONLY',physical['historicalBatch']),
                        ('HISTORICAL_WEB_BYTE_IDENTITY_ONLY',physical['historicalWeb'])):
        for name,digest in domain['physicalClasses'].items():
            role,entry=name.split(':',1)
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in by_path,'every physical nested/metadata class has one verified source owner')
            executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=by_path[path]['owner'],
              qualificationDomain=label,executionSource=domain['source'],executable=executable,
              currentSourceExecutionAccepted=label=='CURRENT_API_QUALIFIED' and executable))
    require(len(rows)==SOURCE_COUNT and len(classes)==ADDED_PHYSICAL and len({r['className'] for r in classes})==ADDED_PHYSICAL
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==CURRENT_EXECUTABLE==len(current['executableClasses']),
      'exact65 sources/57 physical/current3, no historical execution or coverage synthesis')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,witnesses=PINS,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentApiCounters=current['counters'],oldPhysicalBytesUnchanged=1669,
      wholeSourceCountersNotSynthesized=True,coverageUnion=False,default485NotReplaced=True,testsExecutedByTrace=0,
      actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=len(rows),addedPhysical=len(classes),currentExecutable=CURRENT_EXECUTABLE,
      anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
