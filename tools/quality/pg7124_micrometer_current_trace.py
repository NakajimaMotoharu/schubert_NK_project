"""Current32 delta trace, borrowed SDK/POM and current/historical execution domains kept explicit."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SOURCE='ef6f9f22aaa8b16ffcfe39952bfc9a2196b0308a'
SOURCE_COUNT=32
ADDED_PHYSICAL_COUNT=28
CURRENT_TESTS=15
CURRENT_EXECUTABLE=7
WEB_RESULTS=(1574,1575)
OUT=host.BASE/'PG7124-micrometer-current-trace-v1'
PINS={
 'physical':('PG7122-micrometer-http-six-post-v1/manifest.json','9e62721bb5c8d54688d863cf0c5d0cdb1574f63167a638e6672662ad99b877fd'),
 'currentWeb':('PG7118-micrometer-http-post-v3/manifest.json','0aa4cee63e3f64d8b0439edd8b6da776f8a3bd9466e4dbc714f3c28ae7f7518b'),
 'batchHistoryTrace':('PG7092-registry-missing-trace-v1/manifest.json','1f9eeadc6de2aa50692b10353501d07bdfa71e487ad6085136da4445237fae3c')}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists(),'new-only trace, original qualifiers not rewritten')
    witnesses={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact public original qualification pin')
        witnesses[key]=json.loads(file.read_bytes())
    physical=witnesses['physical'];web=witnesses['currentWeb'];history=witnesses['batchHistoryTrace']
    require(physical['source']==web['source']==SOURCE and web['tests']==CURRENT_TESTS and web['actualCrcMismatch']==0,
            'genuine current15 source and actual compiled classes')
    by_path={row['path']:row for row in history['sourceRows']}
    require(len(by_path)==25,'complete historical Batch/config source trace domain')
    documents={int(p.name.partition('_')[0]):p for p in (host.ROOT/'evidence/01_PT/018_NK-OPS-001').glob('*.md')
               if p.name.partition('_')[0].isdigit()}
    def refs(numbers):
        return [dict(path=str(documents[n].relative_to(host.ROOT)),sha256=host.sha(documents[n])) for n in numbers]
    rows=[]
    for item in physical['newSourceDelta']:
        path=item['path'];current=host.ROOT/path
        raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        require(host.sha(current)==item['sha256']==hashlib.sha256(raw).hexdigest(),'each current source exactly fixed candidate byte')
        if path in by_path:
            prior=by_path[path]
            require(prior['sha256']==item['sha256'],'historical source byte identity is explicit, not re-execution')
            row=dict(prior,status=item['status'],qualificationRelationship='HISTORICAL_SOURCE_BYTES_UNCHANGED_NOT_CURRENT_SOURCE_EXECUTION',
                     currentSourceCoverageTransferred=False)
        else:
            name=current.name
            require(path.startswith('src/schubert-nk-web/'),'only the declared Web new-source/pom domain')
            if name=='pom.xml':
                ids='HTTPREC001..009/BUILD';plans=[1573];reports=list(WEB_RESULTS);kind='COMPILE_DEPENDENCY_NOT_EXECUTABLE'
                require(item['status']=='M' and physical['reviewedWebPomChange']['noOtherSemanticChange'],
                        'the one reviewed same-version compile dependency delta')
            elif name.startswith('HttpMetricValve'):
                ids='HTTPTERM001..008';plans=[1577];reports=list(WEB_RESULTS)
                kind='TEST' if name.endswith('Test.java') else 'MAIN'
            elif name.startswith('HttpMetricRecorder'):
                ids='HTTPREC001..009';plans=[1573];reports=list(WEB_RESULTS)
                kind='TEST' if name.endswith('Test.java') else 'MAIN'
            elif name.startswith('HttpMetricContract'):
                ids='HTTPMETRIC001..006';plans=[1570];reports=list(WEB_RESULTS)
                kind='TEST' if name.endswith('Test.java') else 'MAIN'
            elif name=='http-route-labels.txt':
                ids='HTTPMETRIC002/003/HTTPREC003/004';plans=[1570,1573];reports=list(WEB_RESULTS);kind='INDEPENDENT_GOLDEN_RESOURCE'
            else:
                require(name=='package-info.java','only exact declared metadata addition')
                ids='HTTPMETRIC001..006/HTTPREC001..009';plans=[1570,1573];reports=list(WEB_RESULTS);kind='NULLABILITY_METADATA_NOT_EXECUTABLE'
            row=dict(item,kind=kind,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,
              rd='MON005..013',ui='252',ss='313/351',testIdFamily=ids,specifications=refs(plans),results=refs(reports),
              qualificationRelationship='CURRENT_WEB_EXECUTION_OR_DECLARED_SUPPORT_INPUT',
              executionWitness=dict(path=PINS['currentWeb'][0],sha256=PINS['currentWeb'][1],source=SOURCE,tests=CURRENT_TESTS,suites=web['suites']),
              componentCounterScope='EXACT_DECLARED_CURRENT_WEB_EXECUTABLE_CLASSES_ONLY')
        rows.append(row)
    require(len(rows)==SOURCE_COUNT and len({r['path'] for r in rows})==SOURCE_COUNT,'all declared additions and one POM change traced once')
    source_rows={r['path']:r for r in rows};classes=[]
    domains=[('HISTORICAL_BATCH_BYTE_IDENTITY_ONLY',physical['historicalBatch']['source'],physical['historicalBatch']['physicalClasses']),
             ('CURRENT_WEB_QUALIFIED',SOURCE,physical['currentHttp']['physicalClasses'])]
    for domain,source,entries in domains:
        for name,digest in entries.items():
            role,entry=name.split(':',1)
            path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
            require(path in source_rows,'every nested/metadata physical class maps to a declared primary source owner')
            classes.append(dict(className=name,sha256=digest,sourcePath=path,owner=source_rows[path]['owner'],
              qualificationDomain=domain,executionSource=source,executable=not entry.endswith('package-info.class'),
              currentSourceExecutionAccepted=domain=='CURRENT_WEB_QUALIFIED' and not entry.endswith('package-info.class')))
    require(len(classes)==ADDED_PHYSICAL_COUNT and len({r['className'] for r in classes})==ADDED_PHYSICAL_COUNT,'all historical and current physical additions exact')
    require(sum(row['currentSourceExecutionAccepted'] for row in classes)==CURRENT_EXECUTABLE
            ==len(web['executableClasses']),'actual current qualified class flags and raw CRC inventory match the printed count')
    sdk=physical['currentSdkJarHashes']
    require(sdk==web['additionalSdkAuxiliaryJarHashes'] and len(sdk)==4
            and all(host.sha(Path(p))==h for p,h in sdk.items()),'all executed/static/normal-compile SDK dependencies exact')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,witnesses=PINS,
      sourceRows=rows,physicalRows=classes,currentSdkJarHashes=sdk,reviewedWebPomChange=physical['reviewedWebPomChange'],
      oldPhysicalBytesUnchanged=1669,historicalSourceDomainsNotRelabeled=True,
      currentWebCounters=web['counters'],wholeSourceCountersNotSynthesized=True,coverageUnion=False,
      default485NotReplaced=True,testsExecutedByTrace=0,oldSuccessfulTestsRepeated=False,
      actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=SOURCE_COUNT,addedPhysical=ADDED_PHYSICAL_COUNT,currentExecutable=CURRENT_EXECUTABLE,sdkJars=4,
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
