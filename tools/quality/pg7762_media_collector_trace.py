"""Complete115 source/99 physical owners; current Web43, other domains byte-only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7754_media_collector_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7762-media-collector-trace-v1'
SPEC='evidence/01_PT/018_NK-OPS-001/1704_WebMediaStream取得結線_単体テスト仕様書.md'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only trace')
    proofs={};pins={}
    for key,name,digest in (
      ('previous','PG7734-media-stream-trace-v1/manifest.json','b73f72b450b1f21e0e0bd06196b622233fb575692789ca0352e2c1124c05f90f'),
      ('physical','PG7760-media-collector-six-post-v1/manifest.json',None),
      ('currentWeb','PG7758-media-collector-post-v1/manifest.json',None)):
        file=host.BASE/name;sha=host.sha(file);require(digest is None or sha==digest,'original witness hash')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=sha)
    current=proofs['currentWeb'];physical=proofs['physical'];previous={r['path']:r for r in proofs['previous']['sourceRows']}
    require(len(previous)==113 and current['source']==physical['source']==compilation.SOURCE
      and current['tests']==43 and current['suites']==6,'same-source genuine current43')
    spec=dict(path=SPEC,sha256=host.sha(host.ROOT/SPEC));rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(blob).hexdigest()==item['sha256']==host.sha(host.ROOT/path),'committed/current/normal bytes')
        if path in previous:
            row=copy.deepcopy(previous[path]);require(row['sha256']==item['sha256'],'all113 previous source unchanged')
            row.update(previousSourceByteSha256=row['sha256'],sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=False)
        else:
            require(path in {'src/schubert-nk-web/src/'+kind+'/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricCollector'+suffix+'.java'
              for kind,suffix in (('main',''),('test','Test'))},'only new recorder and independent test')
            row=dict(item,kind='TEST' if '/src/test/' in path else 'MAIN',rd='RD171/MON010..013',ui='252',ss='333/351',
              testIdFamily='MEDIACONN001..008',specifications=[spec],previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
        if 'results' in row:row['historicalResults']=row.pop('results')
        if path in current['sourceFiles']:
            require(current['sourceFiles'][path]==item['sha256'],'actual Web source binding')
            row.update(qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_METADATA',componentCounterScope='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY',
              executionWitness=dict(**pins['currentWeb'],source=compilation.SOURCE,tests=43,suites=6))
        elif path.endswith('/pom.xml'):
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',
              compileWitness=dict(**pins['physical'],source=compilation.SOURCE))
        else:row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',componentCounterScope='HISTORICAL_ONLY_NO_CURRENT_COUNTERS')
        row['currentSourceCoverageTransferred']=False;rows.append(row)
    counts=anchors(rows,previous,dict(changed=0,unchanged=113,introduced=2));paths={r['path']:r for r in rows};classes=[]
    for role,key in (('web','currentWeb'),('batch','historicalBatch'),('api','historicalApi')):
        proof=physical[key]
        for name,digest in proof['physicalClasses'].items():
            actual,entry=name.split(':',1);require(actual==role,'physical role')
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in paths,'physical owner exists');executable=not entry.endswith('package-info.class')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=paths[path]['owner'],
              qualificationDomain='CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY',
              executionSource=proof['source'],executable=executable,currentSourceExecutionAccepted=role=='web' and executable))
    require(len(rows)==115 and len(classes)==99 and len({r['className'] for r in classes})==99
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==11,'complete source/physical/current domains')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,sourceRows=rows,physicalRows=classes,
      editAnchorCounts=counts,currentWebCounters=current['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=115,physical=99,currentExecutable=11,anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()

