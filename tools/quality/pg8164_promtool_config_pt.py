"""Official promtool syntax-only on fixed owned public copies; never scrape or server commands."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from host_tool_invocation import capture,verify
import pg8162_promtool_prepare as prepared

ROOT=prepared.ROOT
SLOT=prepared.W/'pg8164-promtool-config-pt-v1'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8164-promtool-config-pt-v1'
PREP_SHA='ca3c93186503b91ff14183b1759b7c8b1e0e33fc73d16685974a8ebd2a01ecae'
BINARY_SHA='4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff'
FILES=('src/deployment/monitoring/prometheus/debug.yml.template',
       'src/deployment/monitoring/prometheus/standard.yml.template')
SPEC='evidence/01_PT/018_NK-OPS-001/1737_Prometheus公式構文parser_単体テスト仕様書.md'
# Independently declared schema-invalid fixtures, not generated expected from production.
NEGATIVE=(
    ('PROMTOOL004','unknown-field.yml',
     {'global':{'scrape_interval':'15s','scrape_timeout':'5s'},'unregistered_root_property':True}),
    ('PROMTOOL005','timeout-greater-interval.yml',
     {'global':{'scrape_interval':'15s','scrape_timeout':'16s'},'scrape_configs':[]}),
    ('PROMTOOL006','duplicate-job.yml',
     {'scrape_configs':[{'job_name':'same-job','static_configs':[{'targets':['127.0.0.1:8081']}]},
                        {'job_name':'same-job','static_configs':[{'targets':['127.0.0.1:8091']}]}]}))


def main():
    invocation=capture(Path(__file__))
    if SLOT.exists() or OUT.exists():
        raise ValueError('new-only syntax PT, existing result needs recovery not replay')
    if prepared.sha(prepared.OUT/'manifest.json')!=PREP_SHA:
        raise ValueError('exact original verified preparation required')
    prep=json.loads((prepared.OUT/'manifest.json').read_bytes())
    if not (prep['actualExit']==0 and prep['toolOnly'] and prep['unselectedMembersExtracted']==0
            and prep['archive']['sha256']==prepared.ARCHIVE_SHA
            and prep['version']['actualExit']==0 and 'version 3.13.5' in prep['version']['stdout']+prep['version']['stderr']):
        raise ValueError('original positive version/archive/ownership receipt required')
    binary=prepared.TOOL/'promtool'
    if binary.is_symlink() or not binary.is_file() or prepared.sha(binary)!=BINARY_SHA:
        raise ValueError('exact verified public binary; no substitute or wrapper')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    input_hashes={p:prepared.sha(ROOT/p) for p in (*FILES,SPEC)}
    for name in FILES:
        tracked=subprocess.check_output(['git','show',source+':'+name],cwd=ROOT)
        if hashlib.sha256(tracked).hexdigest()!=input_hashes[name]:
            raise ValueError('fixed tracked input only, no uncommitted source substituted')
    os.umask(0o077)
    SLOT.mkdir(mode=0o700)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    cases=[dict(testId='PROMTOOL001',result='PASS',actualExit=0,expectedExit=0,
                originalPreparationSha256=PREP_SHA,binarySha256=BINARY_SHA,
                operation='READ_ORIGINAL_ACTUAL_VERSION_CHECKSUM_RECEIPT_NO_REEXECUTION')]
    begin=dict(source=source,invocation=invocation,pid=os.getpid(),startUTC=started,inputHashes=input_hashes,
               originalPreparationSha256=PREP_SHA,binarySha256=BINARY_SHA,
               allowedCommand=['<verified-promtool>','check','config','--syntax-only','<owned-public-copy>'],
               schemaInvalidFixtureExpectedExit=1,environmentSerialized=False)
    prepared.write(SLOT/'begin.safe.json',begin)
    fixtures=[]
    for number,name in enumerate(FILES,2):
        local=SLOT/('debug.yml' if number==2 else 'standard.yml')
        data=(ROOT/name).read_bytes()
        with local.open('xb') as f:
            f.write(data)
        fixtures.append((f'PROMTOOL{number:03d}',local,0,dict(productionPath=name,sha256=input_hashes[name])))
    for test_id,name,data in NEGATIVE:
        local=SLOT/name
        with local.open('x') as f:
            json.dump(data,f,sort_keys=True,allow_nan=False)
            f.write('\n')
        fixtures.append((test_id,local,1,dict(independentFixture=data,sha256=prepared.sha(local))))
    for test_id,file,expected,input_info in fixtures:
        command=[str(binary),'check','config','--syntax-only',str(file)]
        case_start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result=subprocess.run(command,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GOMAXPROCS':'2'},
            stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=30,close_fds=True,check=False)
        row=dict(testId=test_id,command=command,startUTC=case_start,
            endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),input=input_info,
            expectedExit=expected,actualExit=result.returncode,result='PASS' if result.returncode==expected else 'FAIL',
            stdout=result.stdout,stderr=result.stderr,timeoutSeconds=30)
        cases.append(row)
        prepared.write(SLOT/(test_id+'.safe.json'),row)
    if input_hashes!={p:prepared.sha(ROOT/p) for p in input_hashes} or prepared.sha(binary)!=BINARY_SHA:
        raise ValueError('input/tool bytes changed during original syntax PT')
    actual=0 if len(cases)==6 and all(c['result']=='PASS' for c in cases) else 1
    verify(invocation)
    value=dict(actualExit=actual,source=source,invocation=invocation,begin=begin,
        startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        environment=dict(os=platform.platform(),python=platform.python_version(),
                         promtool='3.13.5 linux-amd64',parserMode='check config --syntax-only'),
        tests=6,failed=sum(c['result']!='PASS' for c in cases),errors=0,skipped=0,cases=cases,
        originalPreparation=dict(path=str((prepared.OUT/'manifest.json').relative_to(ROOT)),sha256=PREP_SHA,
                                 preparationToolSource=prep['source'],binarySha256=BINARY_SHA,versionRerun=False),
        inputHashes=input_hashes,fixtureHashes={str(f.relative_to(SLOT)):prepared.sha(f) for _,f,_,_ in fixtures},
        exactOneInvocationPerSyntaxCase=True,syntaxProcesses=5,actualScrapes=0,serviceDiscoveryInvoked=False,
        actualVmActions=0,actualDatabaseActions=0,targetNetworkActions=0,publicArtifactDownloadsByPt=0,
        actualDaemonActions=0,actualCredentialReads=0,referencedSecretOrRuleFilesQualified=False,
        actualEndpointsQualified=False,actualRetentionQualified=False,actualServiceStopQualified=False,
        javaProductTestsExecuted=0,statementCoverage=None,methodCoverage=None,classCoverage=None,branchCoverage=None,
        coverageApplicability='CONFIGURATION_DATA_NOT_EXECUTABLE_JAVA_NO_EXCLUSION',
        whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,bugs=[])
    prepared.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir(mode=0o700)
    prepared.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=actual,source=source,tests=6,failed=value['failed'],
                         manifestSha256=prepared.sha(OUT/'manifest.json'))))
    raise SystemExit(actual)

if __name__=='__main__':
    main()
