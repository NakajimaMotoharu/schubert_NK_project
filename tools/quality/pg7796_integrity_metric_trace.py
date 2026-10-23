"""Complete115 source/103 physical owners; current Web43, other domains byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7804_integrity_metric_six_compile_v2 as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7796-integrity-metric-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1708_BatchIntegrityMetric_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7778-media-bytes-trace-v1/manifest.json','08afec5b1cd6ac4f7fa9c9dc9017f51e33de2d7cdc17e59e8306d1bd83ff096a'),
      ('physical','PG7794-integrity-metric-six-post-v1/manifest.json',None),
      ('currentBatch','PG7790-integrity-metric-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'original witness hash')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    current=proofs['currentBatch'];physical=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==117 and current['source']==physical['source']==compilation.SOURCE
      and current['tests']==253 and current['suites']==33,'same-source genuine current253')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/current/normal bytes')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all117 previous source unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path in {'src/schubert-nk-batch/src/'+kind+'/java/dev/codex/schubert/nk/batch/monitoring/IntegrityFailureMetricRecorder'+suffix+'.java'
              for kind,suffix in (('main',''),('test','Test'))},'only new recorder and independent test')
            row=dict(item,kind='TEST' if '/src/test/' in path else 'MAIN',rd='RD171/MON010..013',ui='252',ss='341/351',
              testIdFamily='INTEGRITYMET001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'actual Batch source binding')
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_BATCH_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=253,suites=33))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=117,introduced=2));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('batch','currentBatch'),('web','historicalWeb'),('api','historicalApi')):
        proof=physical[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'physical owner exists');executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_BATCH_QUALIFIED' if role=='batch' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='batch' and executable))
    require(len(rows)==119 and len(classes)==103 and len({r['className'] for r in classes})==103
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==62,'complete source/physical/current domains')
    dependency=physical['originalCurrentDependency'];dependency_path=dependency['sourcePath']
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owners=[]
    def collect(value):
        if isinstance(value,dict):
            if value.get('path')==dependency_path and value.get('owner'):owners.append(value)
            for item in value.values():collect(item)
        elif isinstance(value,list):
            for item in value:collect(item)
    collect(inventory)
    require(len(owners)==1 and owners[0]['owner']==dependency['owner']=='WBS-P017-02'
      and owners[0]['sha256']==dependency['sourceSha256']==current['sourceFiles'][dependency_path]==host.sha(host.ROOT/dependency_path)
      and dependency_path not in paths and dependency['alreadyInOriginal1669'] is True and dependency['additionalPhysicalCount']==0,
      'unique original dependency source/owner/current byte, not a new source delta or second physical')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentBatchCounters=current['counters'],originalDependencyTrace=dict(**dependency,
        specification=spec,testIdFamily='INTEGRITYMET001',executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=253,suites=33)),
      currentMonitoringExecutables=62,currentOriginalDependencyExecutables=1,wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=119,physical=103,currentExecutable=62,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
