"""Finite disposition of all five raw rows, trace domains and defect closure proof, no PT replay."""
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7144-terminal-quality-review-v1'
PINS={
 'component':('PG7140-http-terminal-post-v2/manifest.json','1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653'),
 'physical':('PG7142-http-terminal-six-post-v1/manifest.json','e29b54744f769b519aec562f6e1bccbcf3535ab448439dd365efcaf07a900ff7'),
 'trace':('PG7150-current-terminal-trace-v2/manifest.json','a4b938d8a1da64e73ffe844680624a98703e264361d55a5ee0b8f2f924f25738')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only review')
    inputs={}
    for name,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'original public proof pin');inputs[name]=json.loads(file.read_bytes())
    component=inputs['component'];trace=inputs['trace'];physical=inputs['physical']
    require(component['source']==trace['source']==physical['source']=='19c777bf3dbe3ddd0286d4c356a00ca8a47c99c5'
      and component['tests']==23 and component['suites']==3 and component['actualCrcMismatch']==0
      and component['actualSessions']==1 and all(v['missed']==0 and v['covered']>0 for v in component['counters'].values()),
      'same-source23/all nine scope actual counters')
    raw=component['staticRaw'];require(raw['pmd']['actualExit']==4 and raw['pmd']['processingErrors']==0
      and all(raw[n]['actualExit']==0 and not raw[n]['findings'] and raw[n]['processingErrors']==0 for n in ('checkstyle','spotbugs')),
      'raw real report exits, no missing-analysis classes')
    rows=[];seen=set()
    for row in raw['pmd']['findings']:
        name,method,rule=row.get('class'),row.get('method'),row['rule']
        if name=='HttpMetricContract.Route' and row.get('variable')=='INDEX' and rule=='AvoidFieldNameMatchingMethodName':
            key='IMMUTABLE_INDEX_FACTORY';disposition='CONTEXT_NOT_APPLICABLE';ids=['HTTPMETRIC002','HTTPMETRIC003']
        else:
            require(name=='HttpMetricValve' and method in ('log','signalFailure') and rule=='AvoidCatchingGenericException',
                    'unknown findings must remain unaccepted')
            kind='RuntimeException' if row['message']=='Avoid catching RuntimeException in try-catch block' else 'Error'
            require(row['message']==f'Avoid catching {kind} in try-catch block','exact actual generic catch kind')
            key=method+':'+kind;disposition='CONTRACT_REQUIRED';ids=['HTTPTERM005','HTTPTERM006','HTTPTERM007']
        require(key not in seen,'each independent finding accounted once');seen.add(key)
        rows.append(dict(key=key,rawFinding=row,disposition=disposition,testIds=ids,reasonDocument='018/1579'))
    require(seen=={'IMMUTABLE_INDEX_FACTORY','log:RuntimeException','log:Error','signalFailure:RuntimeException','signalFailure:Error'},
            'all five raw rows, no suppression/unknown or dropped finding')
    require(len(trace['sourceRows'])==34 and len(trace['physicalRows'])==30
      and sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==9
      and not any('WEB15' in str(r.get('qualificationDomain','')) for r in trace['physicalRows']),
      'corrected exact current nine with count-independent domain labels')
    require(physical['allPhysicalClassCount']==1699 and physical['oldPhysicalUnchanged']==1669
      and physical['historicalBatch']['byteIdentityOnly'] and not physical['historicalBatch']['currentSourceExecutionAccepted'],
      'no old-source PT/coverage ownership transfer')
    value=dict(actualExit=0,source=component['source'],invocation=invocation,witnesses=PINS,
      rawFindings=5,rawPmdExit=4,processingErrors=0,rows=rows,unclassified=0,suppressionsAdded=0,
      actualViolationsOutstanding=0,closedDefectScope=['BUG-1652','BUG-1653','BUG-1654','BUG-1655'],
      closedExpansionScope=['YKT-1405','YKT-1406','YKT-1407','YKT-1408'],
      whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,ptExecutedByReview=0,
      currentSourceCoverageTransferred=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=5,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
