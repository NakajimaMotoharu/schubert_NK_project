"""Independent current POM original4: XML, whole Main absence, Test CRC, immutable public inputs."""
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import jacoco_readonly_exec_subset as decoder
import pg9666_pagination_static as runner
import typed_marker_guard_qualified_v1 as cfg
from trace_owner_join import canonical
import pg17232_runtime_pom_original_four_pt as original

RAW='5cb7518a96dc06de44230517ae68f1314127cc9cc0c3716e51aff7587d749f76'
OUT=data.BASE/'PG17234-runtime-pom-original-four-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17234-runtime-pom-original-four-post-v1'
RUN=original.SLOT
EXPECTED={
 'dev.codex.schubert.nk.batch.bootstrap.BatchRuntimeDependencyTest':[
  'bat283RuntimePostgresDriverAndScopeCanaries',
  'bat283bBootstrapFixtureCannotMaskWrongRuntimeScopeOrDuplicate',
  'bat283cApprovedMonitoringSdkCoordinatesRequireVersionCompileAndMainJar'],
 'dev.codex.schubert.nk.web.bootstrap.WebRuntimeDependencyTest':['scr132RuntimePostgresDriverAndScopeCanaries']}
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only passive qualification')
    raw=data.read_checked(original.OUT/'manifest.json',RAW);require(data.sha((RUN/'manifest.safe.json').read_bytes())==RAW,'original raw byte')
    normal,pin=cfg.normal();prepared=raw['begin'];hashes=normal['begin']['inputHashes']
    require(raw['source']==normal['source']==original.SOURCE and pin==prepared['normalManifestSha256'] and normal['actualExit']==normal['testsExecuted']==0,'current normal compile only')
    require(prepared['sourceHashes']==hashes and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all normal inputs')
    for key in ['dependencyHashes','testSourceHashes']:
        require(all(data.sha(Path(p).read_bytes())==h for p,h in prepared[key].items()),'all original '+key)
    expected_inputs={p:hashes[p] for p in original.POMS};snapshot=original.COMPILE/'snapshot'
    require(all(data.sha((snapshot/p).read_bytes())==h for p,h in expected_inputs.items()),'same frozen public POM reads')
    expected={(b,n) for b,ns in EXPECTED.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE,'genuine current success')
        b=v['begin'];require(b['readOnlyPomInputs']==expected_inputs and b['readOnlySnapshot']==str(snapshot),'same POM snapshot')
        require(b['selectedMethods']==EXPECTED and b['selectedSuites']=={n:len(ns) for n,ns in EXPECTED.items()},'whole fixed Test catalog')
        require((v['tests'],len(v['suites']),v['newTestIds'],v['javaSourceProgramsQualified'])==(4,2,0,0),'four resource-only, no Main credit')
        require(len(v['cases'])==4 and {(c['classname'],c['name']) for c in v['cases']}==expected and all(c['result']=='PASS' for c in v['cases']),'unique whole original pass')
        require(len(v['stages'])==2 and all(type(s['actualExit']) is int and s['actualExit']==0 and s['timedOut'] is False for s in v['stages']),'actual two stages')
        require('-Dnk.pt.repository='+str(snapshot) in v['stages'][1]['command'],'closed original read property')
        require(v['sessionIdentity']==original.SESSION and v['javaCounterCoverageClaimed'] is v['resourceCounterCoverageClaimed'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['effortPercent'] is None,'coverage N/A never100 or formal')
        require(v['productResultsTransferred'] is b['priorProductResultsTransferred'] is False and all(b[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions']),'no transfer or external action')
    contract(raw);negative=[]
    vectors=[
      ('old-source',lambda v:v.update(source='OLD')),
      ('bool-exit',lambda v:v.update(actualExit=True)),
      ('tests',lambda v:v.update(tests=5)),
      ('suite',lambda v:v.update(suites={})),
      ('failed',lambda v:v['cases'][0].update(result='NOT_PASS')),
      ('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),
      ('main-credit',lambda v:v.update(javaSourceProgramsQualified=1)),
      ('coverage',lambda v:v.update(javaCounterCoverageClaimed=True)),
      ('resource-coverage',lambda v:v.update(resourceCounterCoverageClaimed=True)),
      ('formal',lambda v:v.update(formalUpdated=True)),
      ('whole',lambda v:v.update(whole451Accepted=True)),
      ('effort',lambda v:v.update(effortPercent=100)),
      ('timeout',lambda v:v['stages'][1].update(timedOut=True)),
      ('no-poms',lambda v:v['begin'].update(readOnlyPomInputs={})),
      ('foreign-snapshot',lambda v:v['begin'].update(readOnlySnapshot='/foreign')),
      ('partial-methods',lambda v:v['begin'].update(selectedMethods={})),
      ('wrong-counts',lambda v:v['begin'].update(selectedSuites={})),
      ('wrong-property',lambda v:v['stages'][1].update(command=[])),
      ('old-transfer',lambda v:v.update(productResultsTransferred=True)),
      ('vm',lambda v:v['begin'].update(actualVmActions=1))]
    for label,change in vectors:
        bad=copy.deepcopy(raw);change(bad);require(bad!=raw,'nondegenerate negative')
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('false current POM proof '+label)
    actual=[]
    for filename,digest in raw['xmlHashes'].items():
        blob=(RUN/'xml'/filename).read_bytes();require(data.sha(blob)==digest,'original XML hash')
        tree=ET.fromstring(blob);binary=tree.get('name')
        require(binary in EXPECTED and tree.get('tests')==str(len(EXPECTED[binary])) and all(tree.get(k)=='0' for k in ['failures','errors','skipped']),'XML FES0')
        for c in tree.findall('testcase'):
            require(not list(c),'no hidden nonpass');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==4 and set(actual)==expected,'exact original XML identities')
    require((RUN/'xml/summary.safe.txt').read_text()=='found=4;started=4;succeeded=4;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true','genuine no abort/container failure')
    require('-javaagent:'+next(p for p in prepared['dependencyHashes'] if p.endswith('org.jacoco.agent-0.8.15-runtime.jar'))+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION in raw['stages'][1]['command'],'fixed one exec/session')
    own_env={}
    with (RUN/'selected-junit.stdout').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):
                k,v=line.strip().split('=',1);require(k not in own_env,'unique environment');own_env[k]=v
    require(own_env==raw['reportedEnvironment'] and len(own_env)==4,'original own JVM OS/JDK')
    blob=(RUN/'jacoco.exec').read_bytes();require(data.sha(blob)==raw['execSha256'],'exec hash')
    parsed=decoder.decode(blob,set());require(parsed['sessions'][0]['labelBytesHex']==original.SESSION.encode().hex(),'one structural session')
    main={}
    for module,row in normal['jars'].items():
        require(data.sha(Path(row['path']).read_bytes())==row['sha256'],'normal Main jar')
        with zipfile.ZipFile(row['path']) as jar:
            for name in jar.namelist():
                if name.endswith('.class'):
                    require(name[:-6] not in main,'unique full Main physical');main[name[:-6]]=dict(module=module,sha256=data.sha(jar.read(name)))
    require(len(main)==1843,'full Main inventory')
    observed_main=[];true_probes=0
    for name in main:
        try:
            record=decoder.decode(blob,{name})['classes'][name];observed_main.append(name);true_probes+=len(record['hitProbeIds'])
        except ValueError as error:
            require(error.args==('one session and all exact target records required',),'do not hide malformed exec')
    require(true_probes==0,'no Main probe credit')
    SLOT.mkdir();component=SLOT/'test-identity-component';component.mkdir()
    classes=RUN/'fresh-test-classes';test_names=[b.replace('.','/') for b in EXPECTED];test_physical={}
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

    oracles={}
    for binary,(path,count) in original.TEST_PATHS.items():
        text=(data.ROOT/path).read_text()
        require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==EXPECTED[binary] and count==len(EXPECTED[binary]),'whole current original source methods')
        require(all(x in text for x in ['42.7.13','42.7.12','<scope>runtime</scope>','<scope>test</scope>','COMPILE_SCOPE' if 'batch.' in binary else '"compile"']),'independent JDBC literal boundaries')
        if 'batch.' in binary:
            require(all(x in text for x in ['1.17.1','1.17.0','micrometer-core','micrometer-registry-prometheus','foreign.group','foreign','test-jar','0.0.0-foreign']),'independent SDK/fixture oracle')
        oracles[binary]=dict(path=path,sha256=hashes[path],testIds=['PT-BAT-283','PT-BAT-283B','PT-BAT-283C'] if 'batch.' in binary else ['PT-SCR-132'],expectedOrigin='INDEPENDENT_LITERAL_XML_NOT_PRODUCTION_FUNCTION')
    approved={}
    for number in ['311','343','351']:
        paths=list((data.ROOT/'documents/300_SS').glob('**/'+number+'_*.md'));require(len(paths)==1,'unique approved design')
        p=paths[0];relative=str(p.relative_to(data.ROOT));b=p.read_bytes()
        require(b==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same bytes');approved[relative]=data.sha(b)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=[*[p for p,n in original.TEST_PATHS.values()],*original.POMS]
    owners={p:dict(sha256=data.sha((data.ROOT/p).read_bytes()),**canonical(p,logical)) for p in paths}
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for name in raw['xmlHashes']:shutil.copyfile(RUN/'xml'/name,OUT/name)
    data.write(OUT/'main-physical-inventory.safe.json',main)
    result=dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=prepared['normalManifestSha256'],tests=4,suites=2,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,metadataNegativeVectors=len(negative),negativeLabels=negative,readOnlyPomInputs=expected_inputs,allMainPhysical=1843,mainPhysicalInventorySha256=data.sha((OUT/'main-physical-inventory.safe.json').read_bytes()),productionMainRecordsObserved=observed_main,productionMainTrueProbeHits=true_probes,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='NOT_APPLICABLE_NO_MAIN_EXECUTION',testCrcIdentityClasses={v[1]:v[2] for v in rows},testPhysicalHashes=test_physical,passiveTestIdentityStage=stage,passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',reportedEnvironment=own_env,owners=owners,independentOracleVectors=4,literalOracles=oracles,approvedDesignHashes=approved,actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=4,suites=2,metadataNegativeVectors=len(negative),MainCredit=0)))
if __name__=='__main__':main()
