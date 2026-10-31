"""Original full repository/platform enum catalogs; immutable values only, no Unit/SQL actions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import pg6966_chr_adapter_host as host
import pg8122_web_pool_six_compile as compilation
from host_tool_invocation import capture, verify

COMPILE=compilation.SLOT
SOURCE='e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
COMPILE_SHA='75ca9dd88ce045dc0acdbdd878e9382a30584a1da34fb8d37bc04d2ca4d4a53b'
SDK_FILE=host.BASE/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
SDK_SHA='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'
SDK_POST=host.BASE/'PG8173-prometheus-sdk-exact-source-post-v1/manifest.json'
SDK_POST_SHA='a5a2bfbe93bf8b8cc9521b67d1ce4a4c540bc967d7814927b0417807c6b30572'
SLOT=host.W/'pg8178-web-prometheus-gauge-host-v1'
OUT=host.BASE/'PG8178-web-prometheus-gauge-host-v1'
LAUNCHER=host.TC/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
LAUNCHER_SHA='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
AGENT=host.TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
HELPER=host.ROOT/'tools/quality/architecture/WebPrometheusGaugeJunitLauncher.java'
NEW_TEST=host.ROOT/'tools/quality/architecture/WebPrometheusGaugeContractTest.java'
SESSION_ID='PG8178-WEB-PROMETHEUS-GAUGE'
FIXTURE='src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA='1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'
COUNTS={}
TEST_ROOT=host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
FIXTURES={}
EXTRA_TEST_SOURCES=()
TEST_SOURCE_OVERRIDES={}
ENV={'PATH':str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}


def require(value,message):
    if not value:
        raise ValueError(message)



# Exact whole original classes share a simple name; bind and verify by full class name.
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
SLOT=host.W/'pg16477-batch-enum-catalog-original-two-pt-v1'
OUT=host.BASE/'PG16477-batch-enum-catalog-original-two-pt-v1'
HELPER=host.ROOT/'tools/quality/architecture/BatchEnumCatalogTwoCurrentJunitLauncher.java'
REPORTER=host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
COUNTS={"dev.codex.schubert.nk.batch.repository.EnumValueCatalogCompatibilityTest":1,"dev.codex.schubert.nk.batch.platform.EnumValueCatalogCompatibilityTest":1}
TESTS={name:host.ROOT/('src/schubert-nk-batch/src/test/java/'+name.replace('.','/')+'.java') for name in COUNTS}
TEST_PINS={"dev.codex.schubert.nk.batch.repository.EnumValueCatalogCompatibilityTest":"14222dbfc80a510098b3dc85497688f6a863e79a3b1d5722aa4fe2a40bde23a5","dev.codex.schubert.nk.batch.platform.EnumValueCatalogCompatibilityTest":"4455707c599e9fe7ca2265c2bd9f64ca8f81d6705a723dafdc938514cd323939"}
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/batch/repository/BatchStep\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStep.java\",\"sha256\":\"f736e4cf0f251df6b0d0579996b0353e6a757b0def2777a4528ee976c8384285\",\"physical\":{\"dev/codex/schubert/nk/batch/repository/BatchStep\":{\"sha256\":\"06e90b35ca09ac687bfd480caac794fa7be6a47dff9db3d397e682f75f010b1c\",\"code\":true,\"flags\":16433}}},\"dev/codex/schubert/nk/batch/repository/CleanupKind\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupKind.java\",\"sha256\":\"e792d04a7b6409fbfb4696b7b295d242d5958740e084a42bb2f1b3d5592108ea\",\"physical\":{\"dev/codex/schubert/nk/batch/repository/CleanupKind\":{\"sha256\":\"669b9a0ec59d5eabb9264bc525be3ab0e841eabe7b72e9a5530791e8ad560a93\",\"code\":true,\"flags\":16433}}},\"dev/codex/schubert/nk/batch/repository/MaintenanceCompletion\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MaintenanceCompletion.java\",\"sha256\":\"3713fb2ce03a4ec926c4d193051373348da922c15d5f22e8f43cabd215b36dcd\",\"physical\":{\"dev/codex/schubert/nk/batch/repository/MaintenanceCompletion$Outcome\":{\"sha256\":\"a5e9c7c1005bb63c72d4d950f6f628fcb0831f3dcd0881c3be002736189b8c13\",\"code\":true,\"flags\":16433},\"dev/codex/schubert/nk/batch/repository/MaintenanceCompletion\":{\"sha256\":\"876b2a03fc51c860acf7efe94b6287e9e5c87218d42e24bee995b0aee69444ba\",\"code\":true,\"flags\":49}}},\"dev/codex/schubert/nk/batch/platform/ApplicationUnit\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ApplicationUnit.java\",\"sha256\":\"7b48b4c6626835710c612ef868904fa2e10cc7487b24919d9a4141129fbf38f3\",\"physical\":{\"dev/codex/schubert/nk/batch/platform/ApplicationUnit\":{\"sha256\":\"3f2f17a98650fac9a84d440b2e5f6476b79a6e67a8a84d117b0ddc1e5cc565ee\",\"code\":true,\"flags\":16432}}},\"dev/codex/schubert/nk/batch/platform/MaintenanceUnit\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnit.java\",\"sha256\":\"e764ee58aacff2e95fbc30f9102fe40295a25ac0b41df0aaa3ef03a625e34733\",\"physical\":{\"dev/codex/schubert/nk/batch/platform/MaintenanceUnit\":{\"sha256\":\"650b3540616c612413d26e8f3be0c1ced71271b861fb06a1f7e00d1908176453\",\"code\":true,\"flags\":16433}}},\"dev/codex/schubert/nk/batch/platform/RootStartupContext\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/RootStartupContext.java\",\"sha256\":\"8281f715abd82572704c868764f642e10b19e10b4475fd0983735e0fbe340fa8\",\"physical\":{\"dev/codex/schubert/nk/batch/platform/RootStartupContext$Io\":{\"sha256\":\"0f331c2fba47441c7911e3a90a41b73dc9324e8699606e43b3f525b5953f83e5\",\"code\":true,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo$UnitQuery\":{\"sha256\":\"53fe16056a03e57cd6c18051fba5308d2d38f0db78311cb12975d9afcab2b390\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$Snapshot\":{\"sha256\":\"ce86187ba06e6f8a23fe1cc318d7f81cc5d2f96184bebefd6411d5758f4cc3ec\",\"code\":true,\"flags\":49},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo$LinkRead\":{\"sha256\":\"547a7bf046e6ecf91a1b2496b3ba47b726f339ba464c91d13674b939f9189193\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo\":{\"sha256\":\"c4c601773417c7d26e966dbae06df393ee866aa6eac5835f80ccf5b83bd39579\",\"code\":true,\"flags\":48},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$Verification\":{\"sha256\":\"39d7519c5cae53d89094ead71915cbdac613d86f4da314a832612804a059ba0e\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/RootStartupContext$Service\":{\"sha256\":\"f0d2092bd3affc6ee4a015bb0d4ef9008c817d4f3bd349327367b52aa33b3e55\",\"code\":true,\"flags\":16433},\"dev/codex/schubert/nk/batch/platform/RootStartupContext\":{\"sha256\":\"00c87c7af75a74c63fc7bb2debd7d11bdf551b1f9851e25731db837d54801fc5\",\"code\":true,\"flags\":49}}},\"dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.java\",\"sha256\":\"a69a3ab5d53aedde2982176c43bbec15e27358921cd4d5140e395fee228e8cd4\",\"physical\":{\"dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot$Target\":{\"sha256\":\"ce1d0667329660d7f66d29d1fd177f09e9bb9727d2cdec0bf2a9a58fd9e38ad7\",\"code\":true,\"flags\":16433},\"dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot\":{\"sha256\":\"90180d89ef15cacb183ab093e3773b80b7de87ed435c27bd8796c350c45ab48a\",\"code\":true,\"flags\":49}}},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient\":{\"path\":\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/BackupUnitStartClient.java\",\"sha256\":\"505591e7159e2e8d8cb86ffab1e7395ca9d7cdd9e4c796f14d66064a54cd600c\",\"physical\":{\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Intent\":{\"sha256\":\"a1f0b38c5e2e378d8dc51448b2551fd19285fbed96866bd63be02156e6f0e33a\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Target\":{\"sha256\":\"5fe73b91ec4c29b06f0f0a08e147b329c995623de3aa33995ba741612596be72\",\"code\":true,\"flags\":16433},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Policy\":{\"sha256\":\"40ef1782ef235c9a43692a23905c34f5d40ca2669a05959c90d7309e8247d235\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Status\":{\"sha256\":\"3470cf5dc29c46799d355f13fe0f102ccdcbfced95a54ecbba7f536b4bdfb950\",\"code\":true,\"flags\":16433},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Context\":{\"sha256\":\"402475069333a78fe36be64ea70a5915563e08171ba779507a27b84c4ed6fdf4\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Attempt\":{\"sha256\":\"eee477f9264029a68295747a843169695aa9bc6c02934bc1ec0420a0810284fd\",\"code\":true,\"flags\":49},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$RetirementGate\":{\"sha256\":\"3d86cdcc0d578aa06448581d024ec544e6f7e27498f798a079a059532f02a316\",\"code\":false,\"flags\":1537},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$MarkerLease\":{\"sha256\":\"c3b9b7ebf344033ba342c0c6c04459e6cddb217bb1be87e7a6a7596f3ab9e3c1\",\"code\":true,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$1\":{\"sha256\":\"a37f1d054fbf31dc229ae4c8725ae17b8bdd3bc83575bdf592a9dc8480c6f428\",\"code\":true,\"flags\":32},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Start\":{\"sha256\":\"5a653c074e48aa52617cdeb58d68684953c61f449a14366ec13f84673805adb4\",\"code\":false,\"flags\":1536},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient\":{\"sha256\":\"51ad0a4843beada1cabdf74b0491a111eff080f30f89ae062394560a2866dfb8\",\"code\":true,\"flags\":49},\"dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$2\":{\"sha256\":\"53718fa1fe60f094d635bb70f13ca739a4e5ac3bebfc6be56878cf3939747a0b\",\"code\":true,\"flags\":32}}}}")
SESSION_ID='PG16477-BATCH-ENUM-CATALOG-ORIGINAL-TWO'
FIXTURES={}
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
def current_step(name,command):
    # This existing environmental reader references this module's slot through run globals.
    import scoped_prometheus_host as environmental_host
    environmental_host.SLOT=SLOT
    return environmental_step(name,command)
step=current_step

def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only original JVM; existing run is never replayed')
    require(host.sha(COMPILE/'manifest.safe.json')==COMPILE_SHA,'immutable original normal compile witness')
    raw=json.loads((COMPILE/'manifest.safe.json').read_bytes())
    snapshot=COMPILE/'snapshot'
    require(raw['source']==SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
            and raw['testsExecuted']==0,'normal compile-only, never historical PT transfer')
    source_hashes=raw['begin']['inputHashes']
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in source_hashes.items()),
            'all normal frozen input bytes equal current production inputs')
    require(host.sha(SDK_FILE)==SDK_SHA and host.sha(SDK_POST)==SDK_POST_SHA,'exact prepared SDK and independent post witnesses')
    sdk=json.loads(SDK_FILE.read_bytes())
    require(sdk['actualExit']==0 and sdk['newJarCount']==10 and sdk['existingJarCount']==5,'fixed reviewed SDK bundle')
    sdk_jars={row['jar']['path']:row['jar']['sha256'] for row in sdk['downloaded'].values()}
    sdk_jars.update({row['path']:row['sha256'] for row in sdk['reused'].values()})
    require(len(sdk_jars)==15 and all(host.sha(Path(p))==h for p,h in sdk_jars.items()),'all prepared SDK byte pins')
    require(host.sha(LAUNCHER)==LAUNCHER_SHA and AGENT.is_file(),'official existing JUnit and agent')
    cpfile=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt'
    dependencies=[Path(p) for p in cpfile.read_text().strip().split(os.pathsep)]
    external=[p for p in dependencies if '/dev/codex/schubert/' not in str(p)
              and not str(p).startswith(str(snapshot)+'/src/')]
    require(external and all(p.is_file() and str(p).startswith(str(host.TC/'m2/repository')+'/')
                            for p in external),'only actual normal external libraries, no stale internal M2')
    jars=[]
    for item in raw['jars'].values():
        p=Path(item['path'])
        require(host.sha(p)==item['sha256'],'same normal six Main Jar bytes')
        jars.append(p)
    annotation=host.TC/'m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'
    require(host.sha(annotation)=='766ad2a0783f2687962c8ad74ceecc38a28b9f72a2d085ee438b7813e928d0c7',
            'existing compile annotation pin')
    inputs=list(dict.fromkeys([*jars,*external,*[Path(p) for p in sdk_jars],LAUNCHER,annotation]))
    selected=list(TESTS.values())
    test_sources=[*selected,HELPER,REPORTER]
    require(all(p.is_file() for p in test_sources),'closed original sources and reporter')
    require(host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515','qualified reporter byte pin')
    prior=json.loads((host.BASE/'PG16466-current2224-inspector-snapshot-registry-v1/manifest.json').read_bytes())
    require(host.sha(host.BASE/'PG16466-current2224-inspector-snapshot-registry-v1/manifest.json')=='1461c4715e3c1fd53ade29bae01ba03e64d44fecb93cff4f115814d2ecab1d94','previous registry')
    require(prior['source']==SOURCE and all(name not in prior['suiteNames'] for name in COUNTS),'new current-source methods only')
    for name,p in TESTS.items():
        require(host.sha(p)==TEST_PINS[name]==source_hashes[str(p.relative_to(host.ROOT))],'unchanged full original test')
    for row in MAIN_UNITS.values():
        require(host.sha(host.ROOT/row['path'])==source_hashes[row['path']]==row['sha256'],'all eight complete source byte pins')
    resources={}
    for relative,expected in FIXTURES.items():
        file=host.ROOT/relative
        data=subprocess.check_output(['git','show',SOURCE+':'+relative],cwd=host.ROOT)
        require(hashlib.sha256(data).hexdigest()==host.sha(file)==expected,'independent original/current fixture')
        resource_name=relative.split('/src/test/resources/',1)[1]
        require(not Path(resource_name).is_absolute() and '..' not in Path(resource_name).parts,'closed safe resource path')
        resources[resource_name]=(data,expected)
    os.umask(0o077)
    SLOT.mkdir()
    classes=SLOT/'fresh-test-classes'
    classes.mkdir()
    fixture_hashes={}
    for relative,(data,expected) in resources.items():
        destination=classes/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(data)
        require(host.sha(destination)==expected,'exact own independent fixture copy')
        fixture_hashes[str(destination)]=expected
    fixture_hashes.update({str(host.ROOT/p):h for p,h in FIXTURES.items()})
    for p in (classes/'prometheus.properties',SLOT/'empty-prometheus.properties'):
        with p.open('xb'):
            pass
    classpath=os.pathsep.join(str(p) for p in [classes,*inputs])
    begin=dict(source=SOURCE,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
       compileManifestSha256=COMPILE_SHA,normalCompileReplayed=False,priorCoverageTransferred=False,
       archiveSha256=raw['begin']['archiveSha256'],sourceHashes=source_hashes,
       classpathFileSha256=host.sha(cpfile),dependencyHashes={str(p):host.sha(p) for p in [*inputs,AGENT]},
       sdkManifestSha256=SDK_SHA,sdkPostSha256=SDK_POST_SHA,
       testSourceHashes={str(p):host.sha(p) for p in test_sources},selectedSuites=COUNTS,expectedTests=sum(COUNTS.values()),
       fixtureHashes=fixture_hashes,fixtureSource=SOURCE,
       emptyConfigHashes={str(p):host.sha(p) for p in (classes/'prometheus.properties',SLOT/'empty-prometheus.properties')},
       invocation=invocation,environment=ENV,actualVmActions=0,actualDatabaseActions=0,
       actualNetworkActions=0,actualServiceActions=0,rootMainInvoked=False,
       startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    host.write(SLOT/'begin.safe.json',begin)
    jdk=host.TC/'jdk-25.0.4/bin'
    stages=[step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
                                     '-cp',classpath,'-d',str(classes),*[str(p) for p in test_sources]])]
    if stages[0]['actualExit']==0:
        stages.append(step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
          '-Dprometheus.config='+str(SLOT/'empty-prometheus.properties'),
          '-javaagent:'+str(AGENT)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION_ID,
          '-cp',classpath,HELPER.stem,str(SLOT/'xml')]))
    suites={}
    cases=[]
    xml_hashes={}
    for path in sorted((SLOT/'xml').glob('TEST-*.xml')):
        root=ET.parse(path).getroot()
        name=root.get('name')
        simple=name
        require(simple in COUNTS and name not in suites,'exact declared suites only')
        suites[name]={k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        xml_hashes[path.name]=host.sha(path)
        for case in root.findall('testcase'):
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),
                        result='PASS' if not list(case) else 'NOT_PASS',nonPass=[c.tag for c in case]))
    code=stages[-1]['actualExit']
    if code==0:
        require(len(suites)==len(COUNTS) and len(cases)==sum(COUNTS.values()) and len({(c['classname'],c['name']) for c in cases})==sum(COUNTS.values())
                and all(row==dict(tests=COUNTS[n],failures=0,errors=0,skipped=0)
                        for n,row in suites.items()) and all(c['result']=='PASS' for c in cases),
                'all declared actual cases; failed/skipped/not-run never PASS')
    require(all(host.sha(Path(p))==h for p,h in begin['dependencyHashes'].items()),'all actual dependency bytes unchanged')
    require(all(host.sha(Path(p))==h for p,h in begin['testSourceHashes'].items()),'fresh test source unchanged')
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in source_hashes.items()),
            'same source archive/current inputs after original run')
    require(all(host.sha(Path(p))==h for p,h in begin['emptyConfigHashes'].items()),'empty public configs unchanged')
    require(all(host.sha(Path(p))==h for p,h in begin['fixtureHashes'].items()),'independent fixture unchanged after run')
    verify(invocation)
    value=dict(source=SOURCE,actualExit=code,begin=begin,stages=stages,suites=suites,cases=cases,xmlHashes=xml_hashes,
         execSha256=host.sha(SLOT/'jacoco.exec') if (SLOT/'jacoco.exec').exists() else None,
         qualification='RAW_TERMINAL_ONLY_POST_PENDING',whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    host.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=code,tests=len(cases),suites=len(suites),manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(code)


if __name__=='__main__':main()

