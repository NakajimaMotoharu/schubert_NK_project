"""Complete113 source/98 physical owners; current Web35, other domains byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7730_media_stream_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7734-media-stream-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1702_WebMediaStreamMetric_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7718-observed-retention-trace-v1/manifest.json','a0a514b20ce418692402c5164616cc0b01d62c4f83bc73721e6856e345bc465d'),
      ('physical','PG7750-media-stream-six-post-v2/manifest.json',None),
      ('currentWeb','PG7744-media-stream-post-v2/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'original witness hash')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    current=proofs['currentWeb'];physical=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==111 and current['source']==physical['source']==compilation.SOURCE
      and current['tests']==35 and current['suites']==5,'same-source genuine current35')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/current/normal bytes')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all111 previous source unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path in {'src/schubert-nk-web/src/'+kind+'/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricRecorder'+suffix+'.java'
              for kind,suffix in (('main',''),('test','Test'))},'only new recorder and independent test')
            row=dict(item,kind='TEST' if '/src/test/' in path else 'MAIN',rd='RD171/MON010..013',ui='252',ss='333/351',
              testIdFamily='MEDIASTREAM001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'actual Web source binding')
            row.update(qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentWeb'],source=compilation.SOURCE,tests=35,suites=5))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=111,introduced=2));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('web','currentWeb'),('batch','historicalBatch'),('api','historicalApi')):
        proof=physical[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'physical owner exists');executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='web' and executable))
    require(len(rows)==113 and len(classes)==98 and len({r['className'] for r in classes})==98
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==10,'complete source/physical/current domains')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentWebCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=113,physical=98,currentExecutable=10,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
