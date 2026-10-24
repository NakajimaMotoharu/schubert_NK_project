"""Fresh six-Jar complete byte inventory/architecture and exact source-owner trace; no PT replay."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import pg7032_monitoring_six_artifact_post as steps
from host_tool_invocation import capture,verify

SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
BEFORE='e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
COMPILE=host.W/'pg8212-counter-name-six-compile-v1'
SLOT=host.W/'pg8218-counter-name-six-trace-v1'
OUT=host.BASE/'PG8218-counter-name-six-trace-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqMessageMetricRecorder.java'
TEST=MAIN.replace('/main/','/test/').replace('.java','Test.java')
CLASS='api:dev/codex/schubert/nk/api/monitoring/MqMessageMetricRecorder.class'
CONFIGS={
 'src/deployment/monitoring/prometheus/'+n for n in
 ('README.md','debug-arguments.json.template','debug.yml.template','standard.yml.template')}
CONFIGS|={'src/deployment/monitoring/grafana/'+n for n in
 ('README.md','datasources-debug.yml.template','datasources-standard.yml.template','grafana.ini.template')}
WITNESSES=(
 ('normal','PG8212-counter-name-six-compile-v1/manifest.json','db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'),
 ('current','PG8216-counter-name-post-v1/manifest.json','d9796aebcd3d6b9e3a516d5367f02616c1508b6933748b69c5da911ad41e3fb8'),
 ('previous','PG8128-web-pool-six-post-v1/manifest.json','ca562f955fc9140bd4ae0c52f4bec2ef5e70cbd032061ad02e861807ac6c932c'),
 ('original','PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 ('architecture','PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'),
 ('prometheus','PG8140-prometheus-config-pt-v1/manifest.json','25b268f050535f23fd5447083324435e838ce3bb882ae7c99c8273c27b4a8381'),
 ('grafana','PG8156-grafana-config-pt-v1/manifest.json','6359f976bdb3f179983d83b2913a343518eb1f8386cc45faf74dae0e53417a74'))


def require(value,message):
    if not value:
        raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only complete physical proof')
    proofs={}
    pins={}
    for name,path,digest in WITNESSES:
        file=host.BASE/path
        require(host.sha(file)==digest,'full exact immutable '+name+' witness')
        proofs[name]=json.loads(file.read_bytes())
        pins[name]=dict(path=path,sha256=digest)
    normal=proofs['normal']
    current=proofs['current']
    previous=proofs['previous']
    original=proofs['original']
    require(normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0
            and normal['testsExecuted']==0 and current['tests']==40 and current['suites']==5
            and current['actualCrcMismatch']==0 and current['actualSessions']==1
            and len(current['executableClasses'])==6 and all(v['missed']==0 for v in current['counters'].values()),
            'same new source normalcompile/PT and current scope, never old result transfer')
    snapshot=COMPILE/'snapshot'
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in normal['begin']['inputHashes'].items()),
            'all frozen compile/current input bytes')
    before=dict(original['allPhysicalMainSha256'])
    require(len(before)==1669 and previous['source']==BEFORE,'original1669 and actual prior source')
    for role,key in (('web','currentWeb'),('api','historicalApi'),('batch','historicalBatch')):
        rows=previous[key]['physicalClasses']
        rows={role+':'+p:h for p,h in rows.items()} if role=='web' else rows
        require(not(set(before)&set(rows)),'disjoint prior physical owner domains')
        before.update(rows)
    require(len(before)==1799,'complete prior1799, not a partial summary')
    physical={}
    jars={}
    for role,row in normal['jars'].items():
        jar=Path(row['path'])
        require(host.sha(jar)==row['sha256'],'fresh normal Jar bytes')
        jars[role]=jar
        with zipfile.ZipFile(jar) as archive:
            for entry in archive.namelist():
                if entry.endswith('.class'):
                    key=role+':'+entry
                    require(key not in physical,'unique actual physical ownership')
                    physical[key]=hashlib.sha256(archive.read(entry)).hexdigest()
    require(set(jars)==set(architecture.MODULES) and set(physical)==set(before) and len(physical)==1799,
            'all six full Jar class inventories, no missing/added or ignored debug bytes')
    changed={p:dict(beforeSha256=before[p],sha256=h) for p,h in physical.items() if h!=before[p]}
    require(set(changed)=={CLASS} and all(physical[p]==h for p,h in original['allPhysicalMainSha256'].items()),
            'only declared repaired Main changes; all original1669/other1798 physical bytes identical')
    for entry,digest in current['physicalClasses'].items():
        require(physical['api:'+entry]==digest,'every exact current6 executable plus package metadata matches normal API Jar')
    raw=host.W/'pg8214-counter-name-host-v1/manifest.safe.json'
    run=json.loads(raw.read_bytes())
    require(host.sha(raw)==current['originalManifestSha256'] and run['source']==SOURCE,
            'original corrected JVM source and receipt')
    require(all(run['begin']['dependencyHashes'].get(row['path'])==row['sha256'] for row in normal['jars'].values()),
            'original current JVM loads every fresh six Jar, no stale artifact')
    parts=subprocess.check_output(['git','diff','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],
                                  cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'complete current source delta grammar')
    relative={parts[n+1].decode():parts[n].decode() for n in range(0,len(parts),2)}
    require(relative=={MAIN:'M',TEST:'M',**{p:'A' for p in CONFIGS}},
            'only fixed Main/Test change plus eight separately completed monitoring data files')
    for key in ('prometheus','grafana'):
        for path,digest in proofs[key]['inputHashes'].items():
            if path.startswith('src/'):
                require(host.sha(host.ROOT/path)==digest,'same individually verified monitoring config bytes')
    old_rows={r['path']:r for r in previous['newSourceDelta']}
    require(len(old_rows)==147,'all previous147 source ownership rows')
    selected_main=set(current['sourceFiles'])
    selected_tests={p.removeprefix(str(host.ROOT)+'/') for p in run['begin']['testSourceHashes'] if '/src/test/' in p}
    rows=[]
    for path,row in sorted(old_rows.items()):
        digest=host.sha(snapshot/path)
        require(digest==row['sha256'] or path in {MAIN,TEST},'all other145 source delta bytes unchanged')
        relationship='CURRENT_COUNTER_MAIN' if path in selected_main else 'CURRENT_NECESSARY_TEST' if path in selected_tests else 'BYTE_ONLY_NOT_CURRENT_RUN_QUALIFICATION'
        rows.append(dict(path=path,sha256=digest,owner=row.get('owner','WBS-P018-09'),
            previousSha256=row['sha256'],changed=path in {MAIN,TEST},relationship=relationship,
            currentCounterTransferred=False,executionWitness=pins['current'] if relationship.startswith('CURRENT_') else None))
    for path in sorted(CONFIGS):
        rows.append(dict(path=path,sha256=host.sha(snapshot/path),owner='WBS-P018-09',sharedReference='WBS-C07',
            sharedAdditionalCostPp=0,relationship='PREVIOUS_SEMANTIC_CONFIGURATION_BYTES_NOT_RUNTIME_ACCEPTANCE',
            previousSha256=None,changed=False,currentCounterTransferred=False,executionWitness=None))
    require(len(rows)==155 and len({r['path'] for r in rows})==155 and sum(r['changed'] for r in rows)==2,
            'all155 unique source owners, exactly2 existing edits and8 historical configuration additions')
    prior_arch=proofs['architecture']
    require(host.sha(architecture.SOURCE)==prior_arch['toolSourceSha256']
            and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,
            'unchanged previously canary-qualified architecture reader and libraries')
    os.umask(0o077)
    SLOT.mkdir()
    steps.SLOT=SLOT
    classes=SLOT/'audit-classes'
    classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(compiled['actualExit']==0,'pure bytecode reader compile0')
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),
        'ModuleDependencyAudit',*[m+'='+str(jars[m]) for m in architecture.MODULES]])
    analysis=architecture.parse(text)
    require(checked['actualExit']==0 and analysis['physical']==1799 and not analysis['findings']
            and len(analysis['rules'])==5 and all(v==0 for v in analysis['rules'].values()),
            'all fresh physical Main/five exact architecture rules0; no target initialization')
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in normal['begin']['inputHashes'].items()),
            'all source bytes still frozen after static review')
    verify(invocation)
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        witnesses=pins,jars=normal['jars'],allPhysicalClassCount=1799,originalPhysicalUnchanged=1669,
        previousPhysicalUnchanged=1798,physicalChanged=changed,physicalAdded=0,physicalRemoved=0,
        physicalMappingReconstruction='EXACT_PREVIOUS_ALL1799_NAMESPACE_PLUS_DECLARED_SINGLE_CHANGED_SHA; FULL_JARS_PINNED',
        sourceRows=rows,sourceCount=155,currentExecutableScope=sorted(current['executableClasses']),
        currentTests=40,currentSuites=5,currentCounterScope='SIX_CURRENT_API_COUNTER_CLASSES_ONLY',
        currentCounters=current['counters'],coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,
        architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),
        productTestsExecutedByPost=0,canariesReplayed=False,actualVmActions=0,actualDatabaseActions=0,
        actualNetworkActions=0,actualServiceActions=0,newAccepted=0,formalUpdated=False,
        whole451Accepted=False,effortPercent=None,fullRegressionRequiredForFormalAcceptance=True)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1799,changed=len(changed),originalUnchanged=1669,
        sourceRows=len(rows),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
