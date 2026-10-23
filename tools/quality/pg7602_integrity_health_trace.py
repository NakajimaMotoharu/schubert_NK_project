"""Current Batch229/56 and all100 source/88 physical owners, historical API98/Web27 byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7598_integrity_health_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7602-integrity-health-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1687_Integrity供給観測警報_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only role-aware trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7586-restart-health-trace-v1/manifest.json','dcb6d501b7011ef7e4292ba3324a7625296ebd5963a700704587038a2cb4eb9a'),
      ('physical','PG7600-integrity-health-six-post-v1/manifest.json',None),
      ('currentBatch','PG7596-integrity-health-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    physical=proofs['physical'];current=proofs['currentBatch'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==98 and current['source']==physical['source']==compilation.SOURCE and current['tests']==229,'exact current role/source and all prior98')
    rows=[];spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'actual current/frozen/committed source')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all previous98 bytes unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(Path(path).name in {'IntegrityHealthMonitor.java','IntegrityHealthMonitorTest.java'}
              and path.startswith('src/schubert-nk-batch/'),'only two declared new Batch files')
            row=dict(item,kind='TEST' if path.endswith('Test.java') else 'MAIN',rd='MON005..013',ui='252',ss='351',
              testIdFamily='INTEGRITYMON001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'every actual current Batch source input')
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_BATCH_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=229,suites=30))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        if path.startswith('src/schubert-nk-batch/src/main/java/') and Path(path).name in (
          'AlertThresholds.java','AlertLifecycle.java','ObservationContext.java','MonitoringPoller.java','IntegrityHealthMonitor.java'):
            refs=row.setdefault('additionalSpecifications',[])
            if spec not in refs:refs.append(spec)
            row['additionalTestIdFamilies']=list(dict.fromkeys([*row.get('additionalTestIdFamilies',[]),*([row['additionalTestIdFamily']] if 'additionalTestIdFamily' in row else []),'INTEGRITYMON001..008']))
        rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=98,introduced=2));by_path={r['path']:r for r in rows};classes=[]
    for role,key in (('batch','currentBatch'),('api','historicalApi'),('web','historicalWeb')):
        domain=physical[key]
        for name,digest in domain['physicalClasses'].items():
            actual_role,entry=name.split(':',1);require(role==actual_role,'true physical role, no namespace alias')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in by_path,'all physical nested/metadata owners')
            executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=by_path[path]['owner'],
              qualificationDomain='CURRENT_BATCH_QUALIFIED' if role=='batch' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=domain['source'],executable=executable,currentSourceExecutionAccepted=role=='batch' and executable))
    require(len(rows)==100 and len(classes)==88 and len({r['className'] for r in classes})==88
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==56,'all94/88/current48, no historical execution transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentBatchCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=100,physical=88,currentExecutable=56,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
