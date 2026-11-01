"""BUG2232 static official-instrumentation byte witness; target class never loaded."""
from pathlib import Path
import os
import zipfile
import g07_host_class_provenance_inputs as data
import classfile_code_metadata as code
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18318-composite-bytecode-witness-v1'
OUT=data.BASE/'PG18318-composite-bytecode-witness-v1'
NAME='dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration'
def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    target=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot/src/schubert-nk-web/target/classes'/(NAME+'.class')
    with zipfile.ZipFile(normal['jars']['web']['path']) as z:assert target.read_bytes()==z.read(NAME+'.class')
    before=code.decode(target.read_bytes(),NAME+'.class');assert [(r['name'],r['descriptor']) for r in before['methods']]==[('<init>','()V')]
    helper=data.ROOT/'tools/quality/architecture/CoverageDeclaredMethodWitnessV1.java'
    assert data.sha(helper.read_bytes())=='16eee7d2bf9ce7053090fe6457c86dc0462c6691deffd971bdfd38840a2c7112'
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    assert all(data.sha(Path(p).read_bytes())==h for p,h in runtime['toolAndDependencyHashes'].items())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];SLOT.mkdir();runner.SLOT=SLOT;classes=SLOT/'tool-classes';classes.mkdir()
    stages=[]
    stages.append(runner.step('javac',[str(runner.TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(helper)],SLOT,timeout=60))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    output=SLOT/'instrumented-public-config.class'
    stages.append(runner.step('static-instrument-bytes',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(classes)+os.pathsep+cp,'CoverageDeclaredMethodWitnessV1',str(target),str(output)],SLOT,timeout=60))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    after=code.decode(output.read_bytes(),NAME+'.class')
    generated=[m for m in after['methods'] if m['name']!='<init>']
    assert len(generated)==1 and generated[0]['name']=='$jacocoInit' and generated[0]['flags']&4096 and generated[0]['hasCode']
    assert [m for m in after['methods'] if not m['flags']&4096]==before['methods']
    assert (SLOT/'static-instrument-bytes.stdout').read_text()=='TARGET_CLASS_LOADED=false\n'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,helperSha256=data.sha(helper.read_bytes()),normalManifestSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',originalClassSha256=data.sha(target.read_bytes()),instrumentedClassSha256=data.sha(output.read_bytes()),originalClassMetadata=before,instrumentedClassMetadata=after,officialSyntheticMethodsAdded=generated,sourceBusinessMethodCount=0,runtimeInstrumentedNonConstructorMethodCount=1,originalClassesChanged=False,targetProductClassLoaded=False,targetProductMethodsExecuted=0,failedPtReexecuted=False,stages=stages,toolChecksOnly=True,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
