"""Original fixture preflight assertions and actual SDK/adapter metadata; no Product PT replay."""
import ast
import datetime
import json
from pathlib import Path
import re
import pg8844_typed_pool_binding_fixed_host as original
import scoped_prometheus_post as steps
from host_tool_invocation import capture,verify

host=original.run.host
SLOT=host.W/'pg8849-typed-pool-binding-guards-v1'
OUT=host.BASE/'PG8849-typed-pool-binding-guards-v1'
HOST_SHA='321ad03db4fc207dea00beb6023a76e8a5aef9af00b02b3a27e2700bbd71cf9a'
CORE=host.TC/'m2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
CORE_SHA='9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    assert host.sha(Path(original.__file__))==HOST_SHA and host.sha(CORE)==CORE_SHA
    raw_file=host.W/'pg8844-typed-pool-binding-fixed-host-v1/manifest.safe.json'
    assert host.sha(raw_file)=='fafa64a10e6cead62f1509ff9e607a15b3263601b2c6359428ce94820383a435'
    raw=json.loads(raw_file.read_text())
    assert raw['actualExit']==0 and raw['begin']['source']==original.SOURCE
    tree=ast.parse(Path(original.__file__).read_text())
    matched=[node for node in ast.walk(tree) if isinstance(node,ast.If) and ast.unparse(node.test)=="kind == 'DbPoolMetricBinding'"]
    assert len(matched)==1 and len(matched[0].body)==2 and all(isinstance(node,ast.Assert) for node in matched[0].body)
    guard=compile(ast.fix_missing_locations(ast.Module(body=matched[0].body,type_ignores=[])),'<actual-sdk-fixture-preflight-assertions>','exec')
    rejected=[];rows={}
    SLOT.mkdir();steps.SLOT=SLOT
    javap=host.TC/'jdk-25.0.4/bin/javap'
    sdk_receipt,sdk=steps.step('sdk-actual-interfaces',[str(javap),'-classpath',str(CORE),'io.micrometer.core.instrument.simple.SimpleMeterRegistry','io.micrometer.core.instrument.MeterRegistry'])
    assert sdk_receipt['actualExit']==0 and not sdk_receipt['timedOut']
    declarations=[line for line in sdk.splitlines() if line.startswith(('public class io.micrometer.core.instrument.simple.SimpleMeterRegistry ','public abstract class io.micrometer.core.instrument.MeterRegistry '))]
    assert len(declarations)==2 and all('AutoCloseable' not in line for line in declarations) and 'public void close();' in sdk
    for role,title in (('api','Api'),('web','Web')):
        source=host.ROOT/f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{title}DbPoolMetricBindingTest.java'
        assert str(source) in raw['begin']['testSourceHashes'] and host.sha(source)==raw['begin']['testSourceHashes'][str(source)]
        body=source.read_text();exec(guard,{},dict(body=body))
        for name,changed in (('no-auto-closeable',body.replace('implements AutoCloseable','')),('no-close-forward',body.replace('super.close();','')),('raw-sdk-resource',body.replace('new Registry()','new SimpleMeterRegistry()',1)),('missing-registry-owner',body.replace('new Registry()','missingOwner()',1)),('renamed-interface-base',body.replace('class Registry extends SimpleMeterRegistry','class Registry extends Object',1))):
            assert changed!=body
            try: exec(guard,{},dict(body=changed))
            except AssertionError: rejected.append(role+':'+name)
            else: raise AssertionError('actual fixture preflight must reject every mutation')
        adapter=host.W/f'pg8844-typed-pool-binding-fixed-host-v1/fresh-test-classes/dev/codex/schubert/nk/{role}/monitoring/{title}DbPoolMetricBindingTest$Registry.class'
        receipt,text=steps.step(role+'-adapter-metadata',[str(javap),'-p','-c',str(adapter)])
        assert receipt['actualExit']==0 and not receipt['timedOut'] and 'implements java.lang.AutoCloseable' in text
        assert len(re.findall(r'invokespecial.*(?:SimpleMeterRegistry|MeterRegistry)\.close:\(\)V',text))==1
        rows[role]=dict(sourceSha256=host.sha(source),adapterClassSha256=host.sha(adapter),receipt=receipt,oneSdkCloseForward=True)
    assert len(rejected)==10 and host.sha(Path(original.__file__))==HOST_SHA
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,originalHostPreflightSha256=HOST_SHA,originalRawManifestSha256=host.sha(raw_file),sdkCoreSha256=CORE_SHA,sdkDeclarations=declarations,sdkReceipt=sdk_receipt,adapterEvidence=rows,negativeMetadataChecks=rejected,productPtExecuted=0,appClassInitialized=False,coverage=None,formalUpdated=False,newAccepted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,actualFixtureGuardNegatives=10,sdkAdapters=2,productPt=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
