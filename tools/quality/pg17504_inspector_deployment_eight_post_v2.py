"""Independent owned Inspector wrapper8/50 public receipts; child CLI unmeasured, no native/Main credit."""
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
import pg17500_inspector_deployment_eight_pt as original

RAW='7fec86110b87d453a89b3ec57348754664d40248567d2ec6dc5eb7ef40336c57'
OUT=data.BASE/'PG17504-inspector-deployment-eight-post-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg17504-inspector-deployment-eight-post-v2'
RUN=original.SLOT
EXPECTED={'dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest':['renderedShellCheck','statusMapping','malformedReceipts','argumentsAndPlaceholders','realMainBridge','baseUnitAndSyntax','previousProfiles','releaseClasspathAndIsolation']}
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
    expected_inputs={p:hashes[p] for p in original.PUBLIC_FILES};snapshot=original.COMPILE/'snapshot';fixture=RUN/'public-fixture-root'
    require(all(data.sha((snapshot/p).read_bytes())==h for p,h in expected_inputs.items()),'same frozen public POM reads')
    require(all(data.sha((fixture/p).read_bytes())==h for p,h in expected_inputs.items()),'same own public input copies')
    require(all(data.sha(Path(p).read_bytes())==h for p,h in original.TOOLS.items()),'same binary inputs')
    original_text=(data.ROOT/original.TEST_PATHS[next(iter(EXPECTED))][0]).read_text()
    method_pattern=r'@Test\s+void\s+(\w+)\('
    require(re.findall(method_pattern,original_text)==EXPECTED[next(iter(EXPECTED))],'early complete original method catalog')
    method_negative=[]
    for label,value in [('missing-annotation',original_text.replace('@Test','@Disabled')),('changed-method',original_text.replace('void renderedShellCheck','void foreignMethod'))]:
        require(value!=original_text and re.findall(method_pattern,value)!=EXPECTED[next(iter(EXPECTED))],'negative original method catalog '+label);method_negative.append(label)
    import ast
    old_tool=data.ROOT/'tools/quality/pg17502_inspector_deployment_eight_post.py'
    old_tree=ast.parse(old_tool.read_text())
    invalid_patterns=[node.args[0].value for node in ast.walk(old_tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='re' and node.func.attr=='findall' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str)]
    require(len(invalid_patterns)==1,'one actual old invalid literal, no execution/import')
    try:re.compile(invalid_patterns[0])
    except re.error:method_negative.append('old-double-escaped-literal')
    else:raise ValueError('old invalid regex was not independently reproduced')
    require(len(method_negative)==3,'all finite catalog negatives')
    expected={(b,n) for b,ns in EXPECTED.items() for n in ns}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE,'genuine current success')
        b=v['begin'];require(b['readOnlyPublicInputs']==expected_inputs and b['readOnlyFixtureRoot']==str(fixture) and b['normalSnapshotReadOnlyPath']==str(snapshot),'same POM snapshot')
        require(b['selectedMethods']==EXPECTED and b['selectedSuites']=={n:len(ns) for n,ns in EXPECTED.items()},'whole fixed Test catalog')
        require((v['tests'],len(v['suites']),v['newTestIds'],v['javaSourceProgramsQualified'])==(8,1,0,0),'four resource-only, no Main credit')
        require(len(v['cases'])==8 and {(c['classname'],c['name']) for c in v['cases']}==expected and all(c['result']=='PASS' for c in v['cases']),'unique whole original pass')
        require(len(v['stages'])==2 and all(type(s['actualExit']) is int and s['actualExit']==0 and s['timedOut'] is False for s in v['stages']),'actual two stages')
        require('-Dnk.pt.repository='+str(fixture) in v['stages'][1]['command'],'closed original read property')
        require(v['sessionIdentity']==original.SESSION and v['javaCounterCoverageClaimed'] is v['resourceCounterCoverageClaimed'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['effortPercent'] is None,'coverage N/A never100 or formal')
        require(b['ownJavaChildCount']==1 and b['childJavaAgentPresent'] is b['childJavaCoverageClaimed'] is False and b['childBoundarySourceHashes']=={p:hashes[p] for p in original.CHILD_GUARD_FILES},'fixed unadmitted own CLI child, no child coverage/native promotion')
        require(v['originalTopLevelToolReceipts']==len(v['publicReceiptHashes'])==50 and v['actualTotalProcessCount'] is None and v['childJavaCoverageClaimed'] is False,'fifty receipts are not process totals or child coverage')
        require(v['productResultsTransferred'] is b['priorProductResultsTransferred'] is False and all(b[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions']),'no transfer or external action')
    contract(raw);negative=[]
    vectors=[
      ('old-source',lambda v:v.update(source='OLD')),
      ('bool-exit',lambda v:v.update(actualExit=True)),
      ('tests',lambda v:v.update(tests=9)),
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
      ('no-poms',lambda v:v['begin'].update(readOnlyPublicInputs={})),
      ('foreign-snapshot',lambda v:v['begin'].update(readOnlyFixtureRoot='/foreign')),
      ('partial-methods',lambda v:v['begin'].update(selectedMethods={})),
      ('wrong-counts',lambda v:v['begin'].update(selectedSuites={})),
      ('wrong-property',lambda v:v['stages'][1].update(command=[])),
      ('old-transfer',lambda v:v.update(productResultsTransferred=True)),
      ('vm',lambda v:v['begin'].update(actualVmActions=1)),('child-count',lambda v:v['begin'].update(ownJavaChildCount=2)),('child-agent',lambda v:v['begin'].update(childJavaAgentPresent=True)),('child-coverage',lambda v:v.update(childJavaCoverageClaimed=True)),('child-guard-source',lambda v:v['begin'].update(childBoundarySourceHashes={})),('fifty-receipts',lambda v:v.update(publicReceiptHashes={}))]
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
    require(len(actual)==8 and set(actual)==expected,'exact original XML identities')
    require((RUN/'xml/summary.safe.txt').read_text()=='found=8;started=8;succeeded=8;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true','genuine no abort/container failure')
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
    inventory_ref=data.read_checked(data.BASE/'PG17234-runtime-pom-original-four-post-v1/manifest.json','a2bc40501294857ed6f28450eaba36daaff1d11ec1ad9422296bff84065941ef')
    require(inventory_ref['actualExit']==0 and inventory_ref['source']==original.SOURCE and inventory_ref['allMainPhysical']==1843,'same-source existing whole Main inventory')
    inventory_path=data.BASE/'PG17234-runtime-pom-original-four-post-v1/main-physical-inventory.safe.json'
    main=data.read_checked(inventory_path,inventory_ref['mainPhysicalInventorySha256'])
    jar_names=set()
    for module,row in normal['jars'].items():
        require(data.sha(Path(row['path']).read_bytes())==row['sha256'],'normal whole jar unchanged, no new per-class Root hashing')
        with zipfile.ZipFile(row['path']) as jar:
            names={n[:-6] for n in jar.namelist() if n.endswith('.class')}
            require(not jar_names&names,'nonoverlapping normal inventory');jar_names|=names
    require(set(main)==jar_names and len(main)==1843,'existing fixed public class inventory, reused not rehashed')
    observed_main=[];true_probes=0
    for name in main:
        try:
            record=decoder.decode(blob,{name})['classes'][name];observed_main.append(name);true_probes+=len(record['hitProbeIds'])
        except ValueError as error:
            require(error.args==('one session and all exact target records required',),'do not hide malformed exec')
    require(true_probes==0,'no Main probe credit')
    SLOT.mkdir();component=SLOT/'test-identity-component';component.mkdir()
    classes=RUN/'fresh-test-classes';test_names=[next(iter(EXPECTED)).replace('.','/')+suffix for suffix in ['', '$Result']]+['dev/codex/schubert/nk/api/maintenance/UnitSyntaxFixture'];test_physical={}
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
    prior_slot=data.ROOT.parent/'pgpt-runs/PG379/pg17502-inspector-deployment-eight-post-v1'
    require(data.sha(old_tool.read_bytes())=='4df3ff36bfe83e6e49489b8ae27a9c86c4659705ccf1bf488e7b7a3a07e5fe01','immutable failed original post')
    stage=json.loads((prior_slot/'passive-test-crc-exit.safe.json').read_bytes())
    command=[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(prior_slot/'test-identity-component'),*test_names]
    require(stage['command']==command and stage['cwd']==str(prior_slot) and type(stage['actualExit']) is int and stage['actualExit']==0 and stage['timedOut'] is False,'genuine old passive substage only, failed whole remains failed')
    require(all(data.sha((prior_slot/'test-identity-component'/(name+'.class')).read_bytes())==test_physical[name] for name in test_names),'all original component bytes retained')
    for suffix,key in [('stdout','stdoutSha256'),('stderr','stderrSha256')]:require(data.sha((prior_slot/('passive-test-crc.'+suffix)).read_bytes())==stage[key],'original passive output hash')
    rows=[line.split(chr(9)) for line in (prior_slot/'passive-test-crc.stdout').read_text().splitlines() if line.startswith('CLASS'+chr(9))]
    require(len(rows)==3 and {v[1] for v in rows}==set(test_names),'three actual Test identities only, no passive rerun')
    oracles={}
    text=(data.ROOT/original.TEST_PATHS[next(iter(EXPECTED))][0]).read_text()
    require(re.findall(r'@Test\s+void\s+(\w+)\(',text)==EXPECTED[next(iter(EXPECTED))],'whole original eight method source')
    require(all(t in text for t in ['assertEquals(29, receipts.size())','List.of(0, 10, 50, 70)','List.of(1, 70, 143)','new Result(70, "", "")','builder.environment().clear();','return execute(command, Map.of());','UnitSyntaxFixture.environment(directory)','version: 0.11.0','42.7.13','process.waitFor(20, TimeUnit.SECONDS)']),'independent literal outcomes and owned child boundary')
    script=(fixture/'src/deployment/operations/inbox-inspector.sh.template').read_text()
    receipt_vectors=[]
    for status in [0,10,50,70]:
        literal=' '+('NKINSPECTOR1 '+str(status)+chr(10)+'.').encode().hex(' ')
        require(("'"+literal+"'") in script,'independent exact receipt hex literal')
        receipt_vectors.append(dict(status=status,hex=literal))
    outcomes={'renderedShellCheck':[0,0,0],'statusMapping':[0,10,50,70,50,50,50,50,50],'malformedReceipts':[50]*29,'argumentsAndPlaceholders':[70]*3,'realMainBridge':[70],'baseUnitAndSyntax':[0],'previousProfiles':[0]*4,'releaseClasspathAndIsolation':[]}
    by_method={k:[] for k in outcomes}
    for relative,pin in sorted(raw['publicReceiptHashes'].items()):
        path=fixture/relative;require(data.sha(path.read_bytes())==pin,'original owned public command receipt')
        value=json.loads(path.read_bytes());require(value['method'] in outcomes and path.parent.name==value['method'],'exact receipt method')
        by_method[value['method']].append(value['exitCode'])
        if value['method']=='realMainBridge':require(value['stdout']==value['stderr']=='','real rejected empty-env CLI produces no private diagnostic')
    require(by_method==outcomes and sum(map(len,by_method.values()))==50,'all fifty independent original exit vectors, not total OS process count')
    guard={p:(snapshot/p).read_text() for p in original.CHILD_GUARD_FILES}
    require(guard[original.CHILD_GUARD_FILES[0]].index('InspectorLaunchConfiguration.read(arguments, environment)')<guard[original.CHILD_GUARD_FILES[0]].index('factory.create(configuration.settings())'),'empty environment validation precedes native factory')
    require('String root = value(environment, ROOT, 4096);' in guard[original.CHILD_GUARD_FILES[1]] and 'if (value == null' in guard[original.CHILD_GUARD_FILES[1]],'missing configuration has no authority')
    require('if (selected == null) return Optional.empty();' in guard[original.CHILD_GUARD_FILES[3]] and guard[original.CHILD_GUARD_FILES[4]].index('if (profile.isEmpty()) return Optional.empty();')<guard[original.CHILD_GUARD_FILES[4]].index('NativeCoveragePrivateFile.verifyPinnedAgent();'),'no reserved agent has no native private export')
    oracles[next(iter(EXPECTED))]=dict(path=original.TEST_PATHS[next(iter(EXPECTED))][0],sha256=hashes[original.TEST_PATHS[next(iter(EXPECTED))][0]],testIds=['PT-OPS-INBOX-00'+str(i) for i in range(1,9)],receiptHexVectors=receipt_vectors,commandExitVectors=outcomes,expectedOrigin='EXISTING_001_SPEC_EXPLICIT_LITERAL_AND_INDEPENDENT_PYTHON_HEX_NOT_PRODUCTION_FUNCTION')
    approved={}
    for number in ['311','343','351']:
        paths=list((data.ROOT/'documents/300_SS').glob('**/'+number+'_*.md'));require(len(paths)==1,'unique approved design')
        p=paths[0];relative=str(p.relative_to(data.ROOT));b=p.read_bytes()
        require(b==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same bytes');approved[relative]=data.sha(b)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=[*[p for p,n in original.TEST_PATHS.values()],*original.EXTRAS,*original.PUBLIC_FILES]
    owners={p:dict(sha256=data.sha((data.ROOT/p).read_bytes()),**canonical(p,logical)) for p in paths}
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for name in raw['xmlHashes']:shutil.copyfile(RUN/'xml'/name,OUT/name)
    require(data.sha(inventory_path.read_bytes())==inventory_ref['mainPhysicalInventorySha256'],'prior inventory remains immutable')
    for relative,pin in raw['publicReceiptHashes'].items():
        src=fixture/relative;dst=OUT/'commands'/src.parent.name/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);require(data.sha(dst.read_bytes())==pin,'owned sanitized public receipt copy')
    result=dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=prepared['normalManifestSha256'],tests=8,suites=1,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,metadataNegativeVectors=len(negative),negativeLabels=negative,readOnlyPublicInputs=expected_inputs,allMainPhysical=1843,mainPhysicalInventorySha256=inventory_ref['mainPhysicalInventorySha256'],existingMainPhysicalInventoryReference='PG17234-runtime-pom-original-four-post-v1',childBoundarySourceHashes=prepared['childBoundarySourceHashes'],toolBinaryHashes=original.TOOLS,parentProductionMainRecordsObserved=observed_main,parentProductionMainTrueProbeHits=true_probes,parentCoverageScopeOnly=True,childJavaCoverageClaimed=False,ownJavaChildCount=1,childNativeRuntimeTrace=None,childGuardBasis='FIXED_SOURCE_EMPTY_ENV_AND_NO_RESERVED_AGENT_NOT_DYNAMIC_NATIVE_QUALIFICATION',publicToolReceiptCount=50,publicToolReceiptHashes=raw['publicReceiptHashes'],actualTotalProcessCount=None,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='PARENT_NO_MAIN_RECORDS_CHILD_NOT_AGENT_COVERED_NO_CREDIT',testCrcIdentityClasses={v[1]:v[2] for v in rows},testPhysicalHashes=test_physical,passiveTestIdentityStage=stage,passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',reportedEnvironment=own_env,owners=owners,independentOracleVectors=8,methodCatalogNegativeVectors=len(method_negative),methodCatalogNegativeLabels=method_negative,passiveTestCrcReexecuted=False,passiveTestCrcReusedFromFailedWholeSubstage=True,literalOracles=oracles,approvedDesignHashes=approved,actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=8,suites=1,metadataNegativeVectors=len(negative),MainCredit=0)))
if __name__=='__main__':main()
