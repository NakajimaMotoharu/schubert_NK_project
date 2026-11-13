"""Independent metadata cases for the explicit official SDK opt-in. Never Product PT."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,subprocess,sys
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pgpt_artemis_sdk as sdk;import pgpt_closed_host_profile as host
B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');start=ld(B/'input/2147_artemis_sdk_feature_start.json');witness=ld(R/sdk.WITNESS);c=ld(B/'input/2126_log_whole21_qualified_profile.json');inventory={x['path']:x['owner'] for x in ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts']};c.update(id='PG28542-MQ-ORIGINAL26-PROFILE-EXAMPLE',productionCoreMain=start['source'],mainSources=sorted(sdk.MAIN_PATHS),testSources=[dict(path=x['path'],tests=x['tests']) for x in witness['wholeTests']],expectedTests=26,newTestDefinitions=0,sdkJars=sorted(sdk.SDK_PATHS),preparedDependencyHashes={str(host.ANN):sha(host.ANN),str(host.CONSOLE):sha(host.CONSOLE),**{str(sdk.TC/x['path']):x['sha256'] for x in witness['sdkJars']}},productOwnerByMainPath={p:inventory[p] for p in sdk.MAIN_PATHS},reviewedArtemisSdk=dict(witness=ref(R/sdk.WITNESS)),standardCompilerSwitchMaps=[])
c['closureProofs']=list(c['closureProofs'])+[ref(R/sdk.WITNESS)]
physical={}
for name,nested in [('ArtemisAcceptorReadinessClient',['Reader']),('ArtemisAddressSettingsReadinessClient',['Reader','Capacity']),('ArtemisManagementReadinessClient',['OwnedOperation','Reader','Exchange','MessageWriter','OperationEncoder']),('ArtemisManagementReadinessException',[]),('ArtemisQueuePressureClient',['Reader','Pressure','Value','Limits']),('ArtemisReadinessClient',[]),('ArtemisReadinessException',[]),('ArtemisRoleReadinessClient',['Reader']),('ArtemisStartupObservation',['Evidence'])]:
 base='dev/codex/schubert/nk/batch/mq/'+name
 for p in [base,*[base+'$'+n for n in nested]]:physical[p+'.class']=True
for p in ['dev/codex/schubert/nk/storage/StorageIoException','dev/codex/schubert/nk/storage/StorageIoException$Reason','dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard']:physical[p+'.class']=True
assert len(physical)==26;c['physicalClasses']=sorted(physical);c['targetClasses']=['dev/codex/schubert/nk/batch/mq/ArtemisAcceptorReadinessClient','dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation','dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation$Evidence','dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient'];example=B/'input/2148_artemis_sdk_syntax_example_not_execution_profile.json';assert not example.exists();wr(example,c);cases=[]
def run(label,action,fail=False):
 try:action()
 except (ValueError,KeyError,TypeError,AssertionError) as e:
  assert fail,(label,str(e));cases.append(dict(id='SDKMETA'+str(len(cases)+1).zfill(3),case=label,expected='REJECT',actual='REJECT',reason=str(e)))
 else:
  assert not fail,label;cases.append(dict(id='SDKMETA'+str(len(cases)+1).zfill(3),case=label,expected='ACCEPT',actual='ACCEPT'))
def changed(label,mutation):
 x=copy.deepcopy(c);mutation(x);run(label,lambda:host.validate_syntax(x),True)
run('exact optional whole profile syntax',lambda:host.validate_syntax(c))
run('data-only six-JAR witness and current ten-source metadata',lambda:sdk.validate_witness(c,witness,witness['mainInputHashes']))
run('empty optional feature preserves default behavior',lambda:sdk.syntax({}))
for fn in ['2103_jdbc_known_pair8_profile.json','2126_log_whole21_qualified_profile.json']:
 p=B/'input'/fn
 if p.exists():run('legacy syntax no SDK '+fn,lambda p=p:host.validate_syntax(ld(p)))
changed('Artemis without explicit feature remains forbidden',lambda x:x.pop('reviewedArtemisSdk'))
changed('extra official SDK is not implicit fallback',lambda x:x['sdkJars'].append('org/apache/artemis/artemis-selector/2.56.0/artemis-selector-2.56.0.jar'))
changed('native jar rejected',lambda x:x['sdkJars'].__setitem__(0,'io/netty/netty-transport-native-epoll/4.1.137.Final/netty-transport-native-epoll-4.1.137.Final-linux-x86_64.jar'))
changed('server jar rejected',lambda x:x['sdkJars'].__setitem__(0,'org/apache/artemis/artemis-server/2.56.0/artemis-server-2.56.0.jar'))
changed('other version rejected',lambda x:x['sdkJars'].__setitem__(0,x['sdkJars'][0].replace('4.1.137','4.1.136')))
changed('duplicate dependency rejected',lambda x:x['sdkJars'].__setitem__(0,x['sdkJars'][1]))
changed('unknown Main forbidden before file access',lambda x:x['mainSources'].__setitem__(0,sdk.MAIN_BASE+'Unknown.java'))
changed('held native Main forbidden before file access',lambda x:x['mainSources'].__setitem__(0,'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBrokerExecution.java'))
changed('embedded whole Test outside explicit independent set',lambda x:x['testSources'][0].update(path=sdk.TEST_BASE+'ArtemisReadinessClientTest.java'))
changed('selected-method artifact outside whole set',lambda x:x['testSources'][0].update(path=sdk.TEST_BASE+'ExtractedAcceptorTest.java'))
changed('implicit Guard replacement rejected',lambda x:x.pop('reviewedGuardSignature'))
changed('provenance pin path drift rejected',lambda x:x['reviewedArtemisSdk']['witness'].update(path='evidence/other.json'))
changed('provenance not in closure rejected',lambda x:x['closureProofs'].remove(x['reviewedArtemisSdk']['witness']))
for field,value in [('actualExit',1),('productClassesLoadedOrInitialized',True),('productTestsExecuted',1),('realBrokerRootNativeDbCredentialOperations',1),('productCachedClassesOrApplicationJarReads',1),('holdsUnchanged',False)]:
 w=copy.deepcopy(witness);w[field]=value;run('witness rejection '+field,lambda w=w:sdk.validate_witness(c,w,witness['mainInputHashes']),True)
w=copy.deepcopy(witness);w['sdkJars'][0]['sha256']='0'*64;run('dependency hash drift',lambda:sdk.validate_witness(c,w,witness['mainInputHashes']),True)
w=copy.deepcopy(witness);w['mainInputHashes'][c['mainSources'][0]]='0'*64;run('current Main drift',lambda:sdk.validate_witness(c,w,witness['mainInputHashes']),True)
for text in ['new EmbeddedActiveMQ()','ActiveMQClient.createServerLocator("vm://0")','new ClientRequestor(session,"activemq.management")','new RootStartupContext()','ProcessBuilder x','DriverManager.getConnection(x)','Class.forName(x)','thread.join()']:
 run('whole Test source rejects '+text,lambda text=text:sdk.validate_test_text(text),True)
run('pure reader with finite independent worker',lambda:sdk.validate_test_text('Proxy.newProxyInstance(type.getClassLoader(), types, reader); thread.join(10000);'))
for n in sdk.FORBIDDEN_INIT:run('runtime init blocks '+n,lambda n=n:sdk.check_runtime(c,{n}),True)
run('SDK data parser plus real Guard initialization allowed',lambda:sdk.check_runtime(c,{'org/apache/activemq/artemis/api/core/JsonUtil','dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard'}))
# Only the explicitly bounded syntax/input/dependency provenance and post-init guard change.
base='a81ffb6bcb3850f109021e743df40d915fdd7c4b';astproof={}
for path,allowed in [('tools/quality/pgpt_closed_host_profile.py',{'validate_syntax','tool_hashes','checked_inputs'}),('tools/quality/pgpt_closed_host_post.py',{'verify'}),('tools/quality/pgpt_closed_host_stages.py',set())]:
 old=subprocess.check_output(['git','show',base+':'+path],text=True);new=(R/path).read_text();oldnodes={x.name:ast.dump(x,include_attributes=False) for x in ast.parse(old).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))};newnodes={x.name:ast.dump(x,include_attributes=False) for x in ast.parse(new).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))};assert set(oldnodes)==set(newnodes);delta={n for n in oldnodes if oldnodes[n]!=newnodes[n]};assert delta<=allowed,(path,delta);astproof[path]=dict(changedDefinitions=sorted(delta),allOtherDefinitionsIdentical=True,oldSha256=hashlib.sha256(old.encode()).hexdigest(),newSha256=sha(R/path))
# Original normal Product source/Test inputs are still unchanged; the finite Test fix is not applied yet.
for row in witness['wholeTests']:assert sha(R/row['path'])==row['sha256']
O=B/'evidence/PG28520-artemis-sdk-feature-independent-metadata-v1';assert not O.exists();O.mkdir();now=datetime.datetime.now().astimezone().isoformat();m=dict(actualExit=0,atJST=now,metadataCases=cases,caseCount=len(cases),positive=sum(x['actual']=='ACCEPT' for x in cases),negative=sum(x['actual']=='REJECT' for x in cases),astBoundary=astproof,exampleProfile=ref(example),officialSdkWitness=ref(R/sdk.WITNESS),ProductCompileOrExecution=0,sourceOrTestChanged=False,legacyDenialUnchanged=True,rootCompilerAndUnitCommandAndCoverageAlgorithmUnchanged=True,newProductTestDefinitions=0,normal31='NOT_RUN_REQUIRES_BUG2767_FINITE_WORKER_AND_NEW5_SOURCE_PIN',newAcceptance=0,formalUpdated=False,verifier=ref(Path(__file__).resolve()));wr(O/'manifest.json',m)
f=ld(R/start['forecastRef']['path']);assert sha(R/start['forecastRef']['path'])==start['forecastRef']['sha256'];f.update(previousForecast=start['forecastRef'],revision='293-EXACT_ARTEMIS_SDK_FEATURE_METADATA_ONLY',atJST=now)
for k,x in start['estimate'].items():
 f['additionalCompletedWorkPp'][k]=round(f['additionalCompletedWorkPp'][k]+x,3)
 for name in ['additionalDiscoveredRemainingPp','revisedRemainingPp']:f[name][k]=round(f[name][k]-x,3)
tech=dict(kind='EXACT_SIX_OFFICIAL_ARTEMIS_SDK_OPTIN_METADATA_ONLY',evidence=ref(O/'manifest.json'),metadataCases=len(cases),productTestsExecuted=0,newAcceptance=0);f['latestGroupTechnicalResult']=tech;fp=D/'1322_WBS65予実・限定ArtemisSDK工具後版293.json';assert not fp.exists();wr(fp,f);wr(B/'input/2148_artemis_sdk_feature_close.json',dict(groupId=start['groupId'],recordPath=str((D/'1323_WBS65限定ArtemisSDK工具結果.json').relative_to(R)),manifestPath=str((O/'manifest.json').relative_to(R)),manifestSha256=sha(O/'manifest.json'),terminalAtUTC=now,run='PG28520',workIds=start['workIds'],outcome='EXACT_CLIENT_SDK_OPTIN_METADATA_QUALIFIED_NO_PRODUCT_EXECUTION',technical=tech,forecastRef=ref(fp),checkpointText='通常第三者SDK六Jarの明示optinを現十Main/既全六Test＋新fatalTest一つに限定、元backend/native/appJar禁止はdefault不変。metadata'+str(len(cases))+'（正'+str(m['positive'])+'/負'+str(m['negative'])+'）、witness/currentMain/hash/別version-extra-native-serverJar/未reviewMain-Test/無限worker/実factoryinitを拒否。Rootcompiler/全Unitcommand/coverageアルゴリズムは不変、Productcompile/PT0。BUG2768のcategory誤値はPG28517保持→正規start一回event5024を確認、工具guard自体不変更。',nextCommand='PublishSDKfeatureevidence thenstartpricednormal31 .6/1.8/3.6cap5 inclBUG2767finitejoin+original26andnewfatal5 beforeeditingTests. WholeMain10/physical26+realGuard/sourcefixedRootNullAway/fullstatic/independentrawfindingclassification/Gitpin/oncerun/post actualtargetmissesretained (no100fill)/runtimefactory-init0/actual4-Root-native-DB-brokerHOLD. No confirmationreplay ofoldsuccessfulProductTests. Freshquota/usage10:09:02/diskgate.'));print(json.dumps(dict(actualExit=0,metadataCases=len(cases),positive=m['positive'],negative=m['negative'],ProductPT=0,remaining=f['revisedRemainingPp'])))
