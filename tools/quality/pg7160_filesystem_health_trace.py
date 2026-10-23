"""All37 source/32 added physical ownership, current Batch83 vs historical Web/config kept separate."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7160-filesystem-health-trace-v1'
SOURCE='bbc230f8a892d3ad2e47aeaccbe37bbb86bd97b6'
SOURCE_COUNT=37
PREVIOUS_COUNT=34
CURRENT_TESTS=83
CURRENT_SUITES=12
CURRENT_EXECUTABLE=21
ADDED_PHYSICAL=32
REPORTS=(1583,1584)
NEW_SPEC=1582
NEW_TEST_IDS='FSINPUT001..010'
NEW_SS='351'
ALLOWED_NEW_NAMES={'FilesystemHealthObservation.java','FilesystemHealthMonitor.java','FilesystemHealthObservationTest.java'}
EDITED_EXISTING=set()
EXTRA_SPECS={}
EXTRA_TEST_IDS={}
PINS={
 'physical':('PG7158-filesystem-health-six-post-v1/manifest.json','69b2ab7cb63e296a9851c3dd0d34daca4c71b77f841384dc350f1258721dd3a6'),
 'currentBatch':('PG7154-filesystem-health-post-v1/manifest.json','a86ed6ca91bc6df6d9bd886cf7b487a5253176a2f22b55c7b82b31657a5e110f'),
 'previousTrace':('PG7150-current-terminal-trace-v2/manifest.json','a4b938d8a1da64e73ffe844680624a98703e264361d55a5ee0b8f2f924f25738')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only public trace')
    witnesses={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original witness pin');witnesses[key]=json.loads(file.read_bytes())
    physical=witnesses['physical'];current=witnesses['currentBatch'];history=witnesses['previousTrace']
    require(physical['source']==current['source']==SOURCE and current['tests']==CURRENT_TESTS and current['suites']==CURRENT_SUITES
      and current['actualCrcMismatch']==0 and current['actualSessions']==1,'exact current actual-source witness')
    previous={row['path']:row for row in history['sourceRows']};require(len(previous)==PREVIOUS_COUNT,'all prior distinct trace rows')
    docs={int(p.name.partition('_')[0]):p for p in (host.ROOT/'evidence/01_PT/018_NK-OPS-001').glob('*.md')
          if p.name.partition('_')[0].isdigit()}
    def refs(numbers):return [dict(path=str(docs[n].relative_to(host.ROOT)),sha256=host.sha(docs[n])) for n in numbers]
    rows=[];changed=set()
    for item in physical['newSourceDelta']:
        path=item['path'];file=host.ROOT/path
        raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        require(host.sha(file)==item['sha256']==hashlib.sha256(raw).hexdigest(),'each current source exact fixed candidate')
        if path in previous:
            row=dict(previous[path])
            row['previousSourceByteSha256']=previous[path]['sha256']
            row['sourceIntroducedSincePreviousTrace']=False
            if row['sha256']!=item['sha256']:
                require(path in EDITED_EXISTING,'only explicitly planned edits inside prior additions')
                changed.add(path);row['previousSourceByteSha256']=row['sha256']
                row['sourceChangedSincePreviousTrace']=True
                row.update(item)
            else:row['sourceChangedSincePreviousTrace']=False
        else:
            require(path.startswith('src/schubert-nk-batch/') and Path(path).name in ALLOWED_NEW_NAMES,
              'only the declared new source files')
            row=dict(item,kind='DEPENDENCY_DESCRIPTOR' if path.endswith('/pom.xml') else 'TEST' if path.endswith('Test.java') else 'MAIN',rd='MON005..013',ui='252',ss=NEW_SS,
              testIdFamily=NEW_TEST_IDS,specifications=refs([NEW_SPEC]),previousSourceByteSha256=None,
              sourceChangedSincePreviousTrace=False,sourceIntroducedSincePreviousTrace=True)
        if path in EXTRA_SPECS:row['specifications']=list(row.get('specifications',[]))+refs(EXTRA_SPECS[path])
        if path in EXTRA_TEST_IDS:row['testIdFamily']=row.get('testIdFamily','')+'/'+EXTRA_TEST_IDS[path]
        if path.startswith('src/schubert-nk-batch/') and '/monitoring/' in path:
            row.update(qualificationRelationship='CURRENT_BATCH_EXECUTION_OR_DECLARED_SUPPORT_INPUT',
              results=refs(REPORTS),executionWitness=dict(path=PINS['currentBatch'][0],sha256=PINS['currentBatch'][1],source=SOURCE,tests=CURRENT_TESTS,suites=CURRENT_SUITES),
              componentCounterScope='ALL_DECLARED_CURRENT_BATCH_EXECUTABLES_ONLY',currentSourceCoverageTransferred=False)
            if path.endswith('.java'):require(current['sourceFiles'].get(path)==item['sha256'],'all current monitored Java source actually bound to the current execution')
        elif path.endswith('/pom.xml'):
            if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
            row.update(qualificationRelationship='CURRENT_NORMAL_COMPILE_DEPENDENCY_DESCRIPTOR',
              results=refs(REPORTS),compileWitness=dict(path=PINS['physical'][0],sha256=PINS['physical'][1],source=SOURCE),
              componentCounterScope='NOT_EXECUTABLE_CONFIGURATION',currentSourceCoverageTransferred=False)
        else:
            if 'executionWitness' in row:row['historicalExecutionWitness']=row.pop('executionWitness')
            row.update(qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_EXECUTION',
              componentCounterScope='HISTORICAL_WEB_OR_CONFIG_NOT_CURRENT_SOURCE_COUNTERS',currentSourceCoverageTransferred=False)
        rows.append(row)
    require(len(rows)==SOURCE_COUNT and len({r['path'] for r in rows})==SOURCE_COUNT and changed==EDITED_EXISTING,
            'all declared added/changed source owners mapped once, exact planned previous-source edits')
    by_path={row['path']:row for row in rows};classes=[]
    domains=[('CURRENT_BATCH_QUALIFIED',SOURCE,physical['currentBatch']['physicalClasses']),
             ('HISTORICAL_WEB_BYTE_IDENTITY_ONLY',physical['historicalWeb']['source'],physical['historicalWeb']['physicalClasses'])]
    for domain,source,entries in domains:
        for name,digest in entries.items():
            role,entry=name.split(':',1)
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in by_path,'each nested/metadata class has its one source owner')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=by_path[path]['owner'],
              qualificationDomain=domain,executionSource=source,executable=not entry.endswith('package-info.class'),
              currentSourceExecutionAccepted=domain=='CURRENT_BATCH_QUALIFIED' and not entry.endswith('package-info.class')))
    require(len(classes)==ADDED_PHYSICAL and len({r['className'] for r in classes})==ADDED_PHYSICAL
      and sum(r['currentSourceExecutionAccepted'] for r in classes)==CURRENT_EXECUTABLE==len(current['executableClasses']),
      'all declared physical additions, actual current executable count distinct from historical Web nine')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,witnesses=PINS,sourceRows=rows,physicalRows=classes,
      oldPhysicalBytesUnchanged=1669,currentBatchCounters=current['counters'],wholeSourceCountersNotSynthesized=True,
      coverageUnion=False,default485NotReplaced=True,testsExecutedByTrace=0,oldSuccessfulTestsRepeated=False,
      actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=len(rows),addedPhysical=len(classes),currentExecutable=CURRENT_EXECUTABLE,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
