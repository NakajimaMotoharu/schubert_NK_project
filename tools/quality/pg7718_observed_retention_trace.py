"""All111 source/97 physical owners, one declared Mode edit/one Test addition; only current Batch executed."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7714_observed_retention_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7718-observed-retention-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1700_保持設定完全観測_単体テスト仕様書.md'
POLICY='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy.java'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only complete role-aware trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7698-mq-pressure-connection-trace-v1/manifest.json','997c8aaa641e6f48f0fde90cd78e3ed8cffd4349547f77e5e80fe9659ea9af83'),
      ('physical','PG7716-observed-retention-six-post-v1/manifest.json',None),
      ('currentBatch','PG7712-observed-retention-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'exact original public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    physical=proofs['physical'];current=proofs['currentBatch'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==110 and current['source']==physical['source']==compilation.SOURCE and current['tests']==245,'exact current Batch source/test and prior110')
    rows=[];spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/current/normal snapshot exact bytes')
        if path in previous:
            row=copy.deepcopy(previous[path]);changed=row['sha256']!=item['sha256']
            require(changed is (path==POLICY),'only declared existing ModePolicy source edit')
            row.update(sha256=item['sha256'],previousSourceByteSha256=previous[path]['sha256'],sourceChangedSincePreviousTrace=changed,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path=='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/MonitoringRetentionConfigurationTest.java','only one new pure Test file')
            row=dict(item,kind='TEST',rd='MON010..013',ui='252',ss='351',testIdFamily='RETCONF001..008',specifications=[spec],
              previousSourceByteSha256=None,sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'all actual current Batch input bytes')
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_BATCH_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=245,suites=32))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        if path==POLICY:
            refs=row.setdefault('additionalSpecifications',[])
            if spec not in refs:refs.append(spec)
            row['additionalTestIdFamilies']=list(dict.fromkeys([*row.get('additionalTestIdFamilies',[]),'RETCONF001..008']))
        rows.append(row)
    counts=anchors(rows,previous,dict(changed=1,unchanged=109,introduced=1));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('batch','currentBatch'),('api','historicalApi'),('web','historicalWeb')):
        proof=physical[key]
        for name,digest in proof['physicalClasses'].items():
            actual_role,entry=name.split(':',1);require(role==actual_role,'true physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'each physical nested/metadata type owns one source row')
            executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_BATCH_QUALIFIED' if role=='batch' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='batch' and executable))
    require(len(rows)==111 and len(classes)==97 and len({r['className'] for r in classes})==97
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==60,'all111/97/current60, no historical execution transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentBatchCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=111,physical=97,currentExecutable=60,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
