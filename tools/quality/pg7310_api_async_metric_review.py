"""Current API static zero and exact role/source qualification, five independent transfer/provenance guards."""
import copy
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from pg7192_heap_quality_review import anchors

OUT=host.BASE/'PG7310-api-async-metric-review-v1'
PINS={
 'currentApi':('PG7302-api-async-metric-post-v1/manifest.json','246b450c115954b30a6246c71bda7e5a2b25273fea211e32d729eb9b1b0304fa'),
 'physical':('PG7306-api-async-metric-six-post-v1/manifest.json','4d112f8dd1a30644becce423abeeabde2df9d65811736ee08de831f9b9b7491c'),
 'contract':('PG7307-api-metric-contract-review-v1/manifest.json','624e613f9c8ee551d76e5a17a62e44a8ef5d2f89b38a9712673598c55bea9d46'),
 'trace':('PG7308-api-async-metric-trace-v1/manifest.json','381d93ed6e22bece84f3eee23d09a5c6bb37201e741a8e79a43dda34f5bf14ca'),
 'previous':('PG7294-transfer-health-trace-v1/manifest.json','422900508bcbdabcdf26f69a357bb93456b3cc44fdd76301662f7277198b33be')}

def require(value,message):
    if not value:raise ValueError(message)

def domains(rows,classes,current,physical,previous):
    counts=anchors(rows,previous,dict(changed=0,unchanged=61,introduced=4))
    by_path={r['path']:r for r in rows};require(len(classes)==57 and len({r['className'] for r in classes})==57,'all unique physical rows')
    current_inputs=set(current['sourceFiles'])
    for row in rows:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer in any row')
        if path in current_inputs:
            require(row['executionWitness']['source']==current['source'] and row['executionWitness']['tests']==8
              and row['componentCounterScope']=='ALL_CURRENT_API_EXECUTABLES_ONLY'
              and row['sha256']==current['sourceFiles'][path],'current API source exact executed/compiled input only')
        elif not path.endswith('/pom.xml'):
            require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS',
                    'historical source has no current execution witness')
        else:require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],
                     'POM is only the actual current normal compilation descriptor')
    expected={
      'api':('CURRENT_API_QUALIFIED',physical['currentApi']),
      'batch':('HISTORICAL_BATCH_BYTE_IDENTITY_ONLY',physical['historicalBatch']),
      'web':('HISTORICAL_WEB_BYTE_IDENTITY_ONLY',physical['historicalWeb'])}
    for row in classes:
        role,entry=row['className'].split(':',1);label,proof=expected[role]
        executable=not entry.endswith('package-info.class')
        source_path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source']
          and row['currentSourceExecutionAccepted'] is (role=='api' and executable)
          and row['executable'] is executable and row['sha256']==proof['physicalClasses'][row['className']]
          and row['sourcePath']==source_path and row['owner']==by_path[source_path]['owner'],
          'actual role/source/physical bytes/owner and current only API, no aliases')
    require(sum(r['currentSourceExecutionAccepted'] for r in classes)==3==len(current['executableClasses']),
            'actual current flags match exact three qualified executables')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only API static/domain review')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public witness');proofs[key]=json.loads(file.read_bytes())
    current=proofs['currentApi'];physical=proofs['physical'];trace=proofs['trace'];contract=proofs['contract']
    require(current['source']==physical['source']==trace['source']==contract['source']=='72b65394206ac449604e4cffc5d703c55d8fc2f7'
      and current['tests']==8 and current['suites']==1 and current['actualCrcMismatch']==0 and current['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current8 positive four counters/CRC/session/source')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and all(r['actualExit']==0 and not r['findings'] and r['processingErrors']==0
        for r in current['staticRaw'].values()),'actual current API SB/PMD/CS zero')
    require(physical['allPhysicalClassCount']==1726 and physical['oldPhysicalUnchanged']==1669
      and not physical['historicalBatch']['currentSourceExecutionAccepted']
      and not physical['historicalWeb']['currentSourceExecutionAccepted']
      and len(contract['harness']['negativeGuards'])==len(contract['apiPom']['negativeGuards'])==6
      and contract['canonicalDdl']['sourceBytesUnchanged'],'whole physical identities/twelve quality guards/unchanged canonical DDL')
    previous={r['path']:r for r in proofs['previous']['sourceRows']}
    counts=domains(trace['sourceRows'],trace['physicalRows'],current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    api_source=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles'])
    old_source=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
    for label in ('historical-current-flag','role-domain-alias','historical-source-replaced','current-witness-replaced','previous-byte-anchor'):
        rows=copy.deepcopy(trace['sourceRows']);classes=copy.deepcopy(trace['physicalRows'])
        if label=='historical-current-flag':classes[history]['currentSourceExecutionAccepted']=True
        elif label=='role-domain-alias':classes[history]['qualificationDomain']='CURRENT_API_QUALIFIED'
        elif label=='historical-source-replaced':classes[history]['executionSource']=current['source']
        elif label=='current-witness-replaced':rows[api_source]['executionWitness']['source']=physical['historicalBatch']['source']
        else:rows[old_source]['previousSourceByteSha256']='0'*64
        try:domains(rows,classes,current,physical,previous)
        except ValueError:negative.append(dict(kind=label,rejected=True))
        else:raise ValueError('independent source/role/counter-transfer guard accepted mutation')
    value=dict(actualExit=0,source=current['source'],invocation=invocation,witnesses=PINS,
      currentApiStaticFindings=0,currentApiUnclassified=0,suppressionsAdded=0,editAnchorCounts=counts,
      negativeGuards=negative,historicalRawDispositionTransferred=False,currentApiExecutable=3,
      historicalBatchExecutable=42,historicalWebExecutable=9,currentCountersOnly=current['counters'],
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptExecutedByReview=0,
      actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,currentApiFindings=0,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
