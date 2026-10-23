"""Role-aware81-path/69-physical trace, Batch current and API/Web explicitly historical."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7424_batch_generated_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7428-batch-generated-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1656_Batch生成Value契約_追加単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only role-aware trace')
    pins={};proofs={}
    for key,path,digest in (
      ('previous','PG7410-api-generated-contract-trace-v1/manifest.json','3108d74af0d1a4bb8f38532a5ad4fa9f2b9a76a5920ce9ca3d8843c853180939'),
      ('physical','PG7426-batch-generated-byte-bridge-v1/manifest.json',None),
      ('currentBatch','PG7422-batch-generated-post-v1/manifest.json',None)):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original source proof')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    physical=proofs['physical'];current=proofs['currentBatch'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==80 and physical['source']==current['source']==compilation.SOURCE and current['tests']==176,'current role/source not historical alias')
    test='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/GeneratedBatchValueContractTest.java'
    rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];committed=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(committed).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'all source bytes exact')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all prior80 unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path==test,'only one declared new Test')
            row=dict(item,kind='TEST',rd='MON005..013',ui='252',ss='341,351',testIdFamily='GENB001..007',
              specifications=[dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'every current Batch source in executed snapshot')
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_METADATA',
              executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=176,suites=24),
              componentCounterScope='ALL_CURRENT_BATCH_EXECUTABLES_ONLY')
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE),componentCounterScope='NOT_EXECUTABLE_CONFIGURATION')
        else:
            row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',
              componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False
        if path.startswith('src/schubert-nk-batch/src/main/java/') and '/monitoring/' in path:
            row['additionalSpecifications']=[dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC))];row['additionalTestIdFamily']='GENB001..007'
        rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=80,introduced=1));by_path={r['path']:r for r in rows};classes=[]
    for role,domain in (('batch',physical['currentBatch']),('api',physical['historicalApi']),('web',physical['historicalWeb'])):
        for key,digest in domain['physicalClasses'].items():
            actual_role,entry=key.split(':',1);require(actual_role==role,'true physical owner, no role substitution')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in by_path,'every nested physical owner mapped')
            executable=not entry.endswith('package-info.class')
            classes.append(dict(className=key,sha256=digest,sourcePath=path,owner=by_path[path]['owner'],
              qualificationDomain='CURRENT_BATCH_QUALIFIED' if role=='batch' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=domain['source'],executable=executable,currentSourceExecutionAccepted=role=='batch' and executable))
    require(len(classes)==69 and len({r['className'] for r in classes})==69
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==42,'current42/metadata1 and historical26 remain distinct')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentBatchCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=81,physical=69,currentExecutable=42,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
