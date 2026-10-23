"""Complete115 source/105 physical owners; current Web43, other domains byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7818_restart_metric_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7822-restart-metric-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1710_ProcessRestartMetric_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def original_owner(inventory,path,current_sha):
    candidate=inventory['currentPhysicalCandidate']
    require(candidate['source']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
      and inventory['source']=='7fffab57a567914956b66452e5e54388642efdec','explicit current-original and historical source roles')
    current=[(i,r) for i,r in enumerate(candidate['artifacts']) if r.get('path')==path]
    history=[(i,r) for i,r in enumerate(inventory['artifacts']) if r.get('path')==path]
    require(len(current)==len(history)==1,'one target per explicit generation, never recursive flattening')
    index,row=current[0];old_index,old=history[0]
    require(row['kind']==old['kind']=='JAVA' and row['owner']==old['owner']=='WBS-P017-02'
      and row['sha256']==current_sha=='f736e4cf0f251df6b0d0579996b0353e6a757b0def2777a4528ee976c8384285'
      and old['sha256']=='f1394d4e52a1def1708e6ac1fc7b2b5e457b5d0eb1d0f924210c4f5a199865f8',
      'current source hash/owner and separately preserved historical source hash, no source alias')
    return dict(currentLocation=['currentPhysicalCandidate','artifacts',index],historicalLocation=['artifacts',old_index],
      currentOriginalSource=candidate['source'],historicalSource=inventory['source'],owner=row['owner'],
      currentSourceSha256=row['sha256'],historicalSourceSha256=old['sha256'],historicalHashUsedAsCurrent=False)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7810-integrity-metric-trace-v2/manifest.json','8916b963b9bc844588d8057a78c996e8306d9ca0fff00353a7358a4640834cb6'),
      ('physical','PG7820-restart-metric-six-post-v1/manifest.json',None),
      ('currentBatch','PG7816-restart-metric-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'original witness hash')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    current=proofs['currentBatch'];physical=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==119 and current['source']==physical['source']==compilation.SOURCE
      and current['tests']==261 and current['suites']==34,'same-source genuine current261')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/current/normal bytes')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all119 previous source unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path in {'src/schubert-nk-batch/src/'+kind+'/java/dev/codex/schubert/nk/batch/monitoring/ProcessRestartMetricRecorder'+suffix+'.java'
              for kind,suffix in (('main',''),('test','Test'))},'only new recorder and independent test')
            row=dict(item,kind='TEST' if '/src/test/' in path else 'MAIN',rd='RD171/OPS012/MON008,010..013',ui='252',ss='342/351',
              testIdFamily='RESTARTMET001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'actual Batch source binding')
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_BATCH_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=261,suites=34))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=119,introduced=2));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('batch','currentBatch'),('web','historicalWeb'),('api','historicalApi')):
        proof=physical[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'physical owner exists');executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_BATCH_QUALIFIED' if role=='batch' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='batch' and executable))
    require(len(rows)==121 and len(classes)==105 and len({r['className'] for r in classes})==105
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==64,'complete source/physical/current domains')
    dependency=physical['originalCurrentDependency'];dependency_path=dependency['sourcePath']
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    binding=original_owner(inventory,dependency_path,dependency['sourceSha256'])
    require(dependency['owner']==binding['owner'] and current['sourceFiles'][dependency_path]==host.sha(host.ROOT/dependency_path)==dependency['sourceSha256']
      and dependency_path not in paths and dependency['alreadyInOriginal1669'] is True and dependency['additionalPhysicalCount']==0,
      'original dependency current input/owner, not new source or second physical')
    historical=subprocess.check_output(['git','show',binding['historicalSource']+':'+dependency_path],cwd=host.ROOT)
    original=subprocess.check_output(['git','show',binding['currentOriginalSource']+':'+dependency_path],cwd=host.ROOT)
    require(hashlib.sha256(historical).hexdigest()==binding['historicalSourceSha256']
      and hashlib.sha256(original).hexdigest()==binding['currentSourceSha256'],'each declared inventory source generation independently checked in Git')
    target=binding['currentLocation'][-1];metadata_guards=[]
    for name in ('missingCurrent','duplicateCurrent','hashAlias','sourceAlias','ownerAlias','unknownKind'):
        mutant=copy.deepcopy(inventory);items=mutant['currentPhysicalCandidate']['artifacts']
        if name=='missingCurrent':items.pop(target)
        elif name=='duplicateCurrent':items.append(copy.deepcopy(items[target]))
        elif name=='hashAlias':items[target]['sha256']=binding['historicalSourceSha256']
        elif name=='sourceAlias':mutant['currentPhysicalCandidate']['source']=binding['historicalSource']
        elif name=='ownerAlias':items[target]['owner']='WBS-C07'
        else:items[target]['kind']='UNKNOWN'
        try:original_owner(mutant,dependency_path,dependency['sourceSha256'])
        except ValueError:metadata_guards.append(dict(name=name,rejected=True))
        else:raise ValueError('typed-generation metadata mutation accepted')
    require(len(metadata_guards)==6,'all six pure metadata guards, no Product PT or runtime action')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentBatchCounters=current['counters'],
      inventoryGenerationBinding=binding,inventorySha256=host.sha(host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'),
      inventoryGenerationNegativeGuards=metadata_guards,historicalRelatedToolFailure=dict(path='tools/quality/pg7796_integrity_metric_trace.py',
        sha256='ed7f6a1d0be64d8470e96b7b76925fb08d47e845f48f9ce8386a7bfedc66668b',gitVersion='52bc391d8',actualExit=1),
      originalDependencyTrace=dict(**dependency,
        specification=dict(path='evidence/01_PT/018_NK-OPS-001/1708_BatchIntegrityMetric_単体テスト仕様書.md',sha256=host.sha(host.ROOT/'evidence/01_PT/018_NK-OPS-001/1708_BatchIntegrityMetric_単体テスト仕様書.md')),testIdFamily='INTEGRITYMET001',executionWitness=dict(**pins['currentBatch'],source=compilation.SOURCE,tests=261,suites=34)),
      currentMonitoringExecutables=64,currentOriginalDependencyExecutables=1,wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=121,physical=105,currentExecutable=64,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
