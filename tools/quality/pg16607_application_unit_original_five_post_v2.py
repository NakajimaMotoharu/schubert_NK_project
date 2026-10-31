"""Independent resource-only Unit5, four closed public copies and isolated syntax parser; no Main credit."""
import copy
import json
import os
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import jacoco_readonly_exec_subset as decoder
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
from trace_owner_join import canonical
import pg16605_application_unit_original_five_pt_v2 as original
RAW='c4129cc8f24413764004a2422e0a153bb2341fd43641d4a08dcaa80cca0a0e2f'
OUT=data.BASE/'PG16607-application-unit-original-five-post-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg16607-application-unit-original-five-post-v2'
RUN=original.SLOT
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only passive post')
    raw=data.read_checked(original.OUT/'manifest.json',RAW);require(data.sha((RUN/'manifest.safe.json').read_bytes())==RAW,'original raw same byte')
    normal,pin=cfg.normal();prepared=raw['begin'];hashes=normal['begin']['inputHashes']
    require(raw['source']==normal['source']==original.SOURCE and pin==prepared['normalManifestSha256'] and normal['actualExit']==normal['testsExecuted']==0,'current compile only')
    require(prepared['sourceHashes']==hashes and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'same entire frozen normal source inputs')
    for key in ['dependencyHashes','testSourceHashes','publicResourceCopies']:require(all(data.sha(Path(p).read_bytes())==h for p,h in prepared[key].items()),'same original '+key)
    expected_inputs={n:hashes[n] for n in original.RESOURCES}
    classes=RUN/'fresh-test-classes';repo=RUN/'public-repository'
    expected_copies={str(repo/n):expected_inputs[n] for n in original.RESOURCES}
    require(not repo.is_symlink() and {str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file()}==set(original.RESOURCES),'closed four public repository copies')
    excluded={row['path'] for row in normal['jars'].values()}
    agent=prepared['jacocoAgent'];require(data.sha(Path(agent['path']).read_bytes())==agent['sha256'],'fixed separate instrumentation agent')
    syntax=prepared['syntaxTool'];require(syntax==dict(path='/usr/bin/systemd-analyze',sha256='188138cf3aea2111c7744069b58c0597559808163d1b7f74ded0348d85e4bef3') and data.sha(Path(syntax['path']).read_bytes())==syntax['sha256'],'fixed public syntax tool')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE,'actual current success')
        b=v['begin'];require(b['publicResourceInputs']==expected_inputs and b['publicResourceCopies']==expected_copies,'same seven source/copy/definition bindings')
        require((v['tests'],len(v['suites']),v['newTestIds'],v['javaSourceProgramsQualified'])==(5,1,0,0),'four resource-only, no Main credit')
        require(len(v['cases'])==5 and len({(r['classname'],r['name']) for r in v['cases']})==5 and all(r['result']=='PASS' for r in v['cases']),'all original nonduplicate pass')
        require(len(v['stages'])==3 and all(type(s['actualExit']) is int and s['actualExit']==0 and s['timedOut'] is False for s in v['stages']),'two actual owned stages')
        require(v['sessionIdentity']==original.SESSION and v['javaCounterCoverageClaimed'] is v['resourceCounterCoverageClaimed'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['effortPercent'] is None,'no zero-scope100/acceptance')
        require(b['publicRepository']==str(repo) and b['excludedProductionMainJars']==sorted(excluded) and b['classpathEntries'][0]==str(classes) and not set(b['classpathEntries'])&excluded and all(x in b['dependencyHashes'] for x in b['classpathEntries'][1:]),'external-only classpath, no Main jars')
        require(b['jacocoAgent']==agent and b['syntaxTool']==syntax and b['actualManagerServiceActions']==0,'agent/CP/tool domains')
        require(v['productResultsTransferred'] is b['priorProductResultsTransferred'] is False and all(b[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions']),'no transfer or external actions')
    contract(raw);negative=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('bool-exit',lambda v:v.update(actualExit=True)),('tests',lambda v:v.update(tests=v['tests']+1)),('failed',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('main-credit',lambda v:v.update(javaSourceProgramsQualified=1)),('coverage',lambda v:v.update(javaCounterCoverageClaimed=True)),('resource-coverage',lambda v:v.update(resourceCounterCoverageClaimed=True)),('formal',lambda v:v.update(formalUpdated=True)),('whole',lambda v:v.update(whole451Accepted=True)),('effort',lambda v:v.update(effortPercent=100)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('no-inputs',lambda v:v['begin'].update(publicResourceInputs={})),('no-copies',lambda v:v['begin'].update(publicResourceCopies={})),('main-cp',lambda v:v['begin']['classpathEntries'].append(sorted(excluded)[0])),('agent-bad',lambda v:v['begin']['jacocoAgent'].update(sha256='0'*64)),('old',lambda v:v.update(productResultsTransferred=True)),('vm',lambda v:v['begin'].update(actualVmActions=1)),('tool-bad',lambda v:v['begin']['syntaxTool'].update(sha256='0'*64)),('repo-bad',lambda v:v['begin'].update(publicRepository='/foreign'))]:
        bad=copy.deepcopy(raw);change(bad);require(bad!=raw,'nondegenerate negative '+label)
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('false resource-only qualification '+label)
    actual=[]
    for filename,pin_xml in raw['xmlHashes'].items():
        blob=(RUN/'xml'/filename).read_bytes();require(data.sha(blob)==pin_xml,'original XML hash');xml=ET.fromstring(blob)
        require(xml.get('tests')=='5' and all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'actual XML FES0')
        for c in xml.findall('testcase'):require(not list(c),'no hidden nonpass');actual.append((c.get('classname'),c.get('name')))
    expected={(original.NAME,n) for n in ['apiDependencyCredentialAndResourceContract','webDependencyCredentialAndResourceContract','noSecretInEnvironmentOrShellAndNoAutomaticWritableEscalation','renderedSyntaxIsAcceptedWithoutStartingService','isolatedLookupStillReportsProjectSyntaxWarnings']}
    require(len(actual)==5 and set(actual)==expected=={(v['classname'],v['name']) for v in raw['cases']},'whole fixed original identities')
    require((RUN/'xml/summary.safe.txt').read_text()=='found=5;started=5;succeeded=5;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true','no abort/container false success')
    require('-javaagent:'+agent['path']+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION in raw['stages'][2]['command'],'original fixed exec/session command')
    own_env={}
    with (RUN/'selected-junit.stdout').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):k,v=line.strip().split('=',1);require(k not in own_env,'unique original env');own_env[k]=v
    require(own_env==raw['reportedEnvironment'] and len(own_env)==4,'actual original JVM prefix')
    blob=(RUN/'jacoco.exec').read_bytes();require(data.sha(blob)==raw['execSha256'],'original immutable exec')
    parsed=decoder.decode(blob,set());require(parsed['sessions'][0]['labelBytesHex']==original.SESSION.encode().hex(),'single structurally valid original session')
    main={}
    for module,row in normal['jars'].items():
        with zipfile.ZipFile(row['path']) as jar:
            require(data.sha(Path(row['path']).read_bytes())==row['sha256'],'normal jar identity')
            for name in jar.namelist():
                if name.endswith('.class'):
                    require(name[:-6] not in main,'no duplicate Main physical names')
                    main[name[:-6]]=dict(module=module,sha256=data.sha(jar.read(name)))
    require(len(main)==1843,'normal full Main physical inventory')
    observed_main=[];true_probes=0
    for name in main:
        try:
            record=decoder.decode(blob,{name})['classes'][name];observed_main.append(name);true_probes+=len(record['hitProbeIds'])
        except ValueError as error:
            require(error.args==('one session and all exact target records required',),'no malformed/duplicate target hidden as absence')
    require(true_probes==0,'no Production Main executed probe, no Java Source credit')
    SLOT.mkdir();component=SLOT/'test-identity-component';component.mkdir();test_names=['dev/codex/schubert/nk/api/maintenance/ApplicationServiceUnitTest','dev/codex/schubert/nk/api/maintenance/UnitSyntaxFixture'];test_physical={}
    for name in test_names:
        source=classes/(name+'.class');target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);test_physical[name]=data.sha(source.read_bytes())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b');cp=receipt['command'][2]
    reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    require(data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3','existing qualified passive reader class')
    require(data.sha((data.ROOT/'tools/quality/architecture/WholeSourceCoverageMeasureV1.java').read_bytes())=='97cecbbff82e9c93d41f13e94872b792f374f84d34973a930daefb79bb7be260','reader Source exact')
    tool_proof=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(all(data.sha(Path(p).read_bytes())==h for p,h in tool_proof['toolAndDependencyHashes'].items()),'original reader tool dependencies')
    cp_entries=cp.split(os.pathsep);audit=Path(cp_entries[0]);compiled=tool_proof['reusedCompiledClasses']
    require(set(cp_entries[1:])=={p for p in tool_proof['toolAndDependencyHashes'] if p.endswith('.jar')} and len(cp_entries)==5,'closed existing reader runtime')
    require({p.name for p in audit.iterdir()}==set(compiled) and all(data.sha((audit/n).read_bytes())==h for n,h in compiled.items()),'existing audit classes unchanged')
    runner.SLOT=SLOT;stage=runner.step('passive-test-crc',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*test_names],SLOT,timeout=120)
    require(stage['actualExit']==0 and not stage['timedOut'],'fresh Test CRC/session, not Main coverage')
    rows=[line.split('\t') for line in (SLOT/'passive-test-crc.stdout').read_text().splitlines() if line.startswith('CLASS\t')]
    require(len(rows)==2 and {v[1] for v in rows}==set(test_names),'two actual Test identities only')
    test=original.TEST.read_text();fixture=original.FIXTURE.read_text()
    require(data.sha(original.TEST.read_bytes())==original.TEST_SHA and data.sha(original.FIXTURE.read_bytes())==original.FIXTURE_SHA,'whole original Test and helper')
    vectors=[['"2048M", "60s", "512m", "1024m", "256m", "256m"','"1536M", "30s", "384m", "768m", "128m", "192m"'],['"schubert schubert-read schubert-web"','"schubert schubert-read"','"operation-hmac-current"','"web-session-aes-current"'],['assertFalse(line.startsWith("Environment="))','assertFalse(line.contains("SetCredential="))','assertFalse(line.contains("PassEnvironment="))'],['unit.replace(executable, "ExecStart=/bin/true")','running.waitFor(Duration.ofSeconds(10))','assertEquals("", output)'],['Unknown key \'NKInvalidDirectiveForNegativeOracle\'','assertTrue(output.contains("negative.service"))','assertFalse(output.contains("xfs_scrub_all.service"))']]
    require(all(all(v in test for v in group) for group in vectors),'five independent directive/negative/syntax oracles')
    require('return Map.of("SYSTEMD_UNIT_PATH", directory.toString(), "LC_ALL", "C")' in fixture and 'List.of("sysinit", "basic", "shutdown")' in fixture,'only own Unit paths and implicit target stubs')
    tool_version=(RUN/'syntax-tool-version.stdout').read_bytes();require(tool_version.startswith(b'systemd 259 (259.9-0ubuntu0.1)') and raw['stages'][1]['command']==[str(original.TOOL),'--version'],'actual syntax tool version')
    design={}
    for number in ['342','343']:
        paths=list((data.ROOT/'documents/300_SS/340_batch・基盤').glob(number+'_*.md'));require(len(paths)==1,'unique approved SS');relative=str(paths[0].relative_to(data.ROOT));approved=paths[0].read_bytes()
        require(approved==__import__('subprocess').check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same byte');design[relative]=data.sha(approved)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=[str(original.TEST.relative_to(data.ROOT)),str(original.FIXTURE.relative_to(data.ROOT)),*original.RESOURCES]
    owners={p:dict(sha256=data.sha((data.ROOT/p).read_bytes()),**canonical(p,logical)) for p in paths}
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for name in raw['xmlHashes']:shutil.copyfile(RUN/'xml'/name,OUT/name)
    data.write(OUT/'main-physical-inventory.safe.json',main)
    result=dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=prepared['normalManifestSha256'],tests=5,suites=1,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,metadataNegativeVectors=len(negative),negativeLabels=negative,publicResourceInputs=expected_inputs,publicResourceCopies=expected_copies,publicRepository=str(repo),excludedProductionMainJars=sorted(excluded),jacocoAgent=agent,syntaxTool=syntax,syntaxToolVersionSha256=data.sha(tool_version),independentOracleVectors=len(vectors),ownSyntaxParserInvocationsDeclared=3,actualManagerServiceActions=0,allMainPhysical=1843,mainPhysicalInventorySha256=data.sha((OUT/'main-physical-inventory.safe.json').read_bytes()),productionMainRecordsObserved=observed_main,productionMainTrueProbeHits=true_probes,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='NOT_APPLICABLE_NO_MAIN_EXECUTION',testCrcIdentityClasses={v[1]:v[2] for v in rows},testPhysicalHashes=test_physical,passiveTestIdentityStage=stage,passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',reportedEnvironment=own_env,owners=owners,approvedDesignHashes=design,actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=result['actualExit'],tests=result['tests'],suites=result['suites'],mainProgramsQualified=result['javaSourceProgramsQualified'])))
if __name__=='__main__':main()
