"""Metadata-only recovery of already completed byte instrumentation; never rerun it."""
import copy
import json
import zipfile
import g07_host_class_provenance_inputs as data
import classfile_code_metadata as code
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD=data.ROOT.parent/'pgpt-runs/PG379/pg18318-composite-bytecode-witness-v1'
OUT=data.BASE/'PG18318-composite-bytecode-witness-v2'
NAME='dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration'
def require(ok,reason):
    if not ok:raise ValueError(reason)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    require(data.sha((data.ROOT/'tools/quality/pg18318_composite_bytecode_witness.py').read_bytes())=='4cc7f723ae8d54bdceff7e6fb15c90b7f465a94f1c1ed54a6df6cf8b324ea34e','old failed source retained')
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'normal source')
    target=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot/src/schubert-nk-web/target/classes'/(NAME+'.class')
    with zipfile.ZipFile(normal['jars']['web']['path']) as z:require(z.read(NAME+'.class')==target.read_bytes(),'exact original class')
    before=code.decode(target.read_bytes(),NAME+'.class');after=code.decode((OLD/'instrumented-public-config.class').read_bytes(),NAME+'.class')
    helper=data.ROOT/'tools/quality/architecture/CoverageDeclaredMethodWitnessV1.java'
    require(data.sha(helper.read_bytes())=='16eee7d2bf9ce7053090fe6457c86dc0462c6691deffd971bdfd38840a2c7112','unchanged helper')
    stages=[]
    for label in ['javac','static-instrument-bytes']:
        stage=json.loads((OLD/(label+'-exit.safe.json')).read_bytes())
        require(stage['actualExit']==0 and stage['timedOut'] is False and stage['cwd']==str(OLD),'genuine completed stage')
        require(stage['stdoutSha256']==data.sha((OLD/(label+'.stdout')).read_bytes()) and stage['stderrSha256']==data.sha((OLD/(label+'.stderr')).read_bytes()),'completed output hashes')
        stages.append(dict(stage=stage,receiptSha256=data.sha((OLD/(label+'-exit.safe.json')).read_bytes())))
    require(stages[0]['stage']['command'][-1]==str(helper) and stages[1]['stage']['command'][-2:]==[str(target),str(OLD/'instrumented-public-config.class')],'exact bounded original commands')
    def identity(m):return {k:m[k] for k in ['name','descriptor','flags','hasCode']}
    def contract(a,b):
        ordinary=[m for m in b['methods'] if not m['flags']&4096]
        generated=[m for m in b['methods'] if m['flags']&4096]
        require([identity(m) for m in ordinary]==[identity(m) for m in a['methods']],'normal method identity unchanged')
        require(len(a['methods'])==1 and a['methods'][0]['name']=='<init>' and len(generated)==1 and generated[0]['name']=='$jacocoInit' and generated[0]['hasCode'],'official synthetic augmentation')
        require(ordinary[0]['codeLength']>a['methods'][0]['codeLength'],'constructor probe Code increment disclosed')
    contract(before,after);negative=[]
    for label,change in [('method-identity',lambda v:v['methods'][0].update(name='foreign')),('code-length-assumed-equal',lambda v:v['methods'][0].update(codeLength=before['methods'][0]['codeLength'])),('synthetic-erased',lambda v:v['methods'][-1].update(flags=v['methods'][-1]['flags']&~4096))]:
        bad=copy.deepcopy(after);change(bad)
        try:contract(before,bad)
        except ValueError:negative.append(label)
        else:raise ValueError('false bytecode witness')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalClassSha256=data.sha(target.read_bytes()),instrumentedClassSha256=data.sha((OLD/'instrumented-public-config.class').read_bytes()),originalClassMetadata=before,instrumentedClassMetadata=after,sourceBusinessMethodCount=0,runtimeInstrumentedNonConstructorMethodCount=1,staticNegativeVectors=len(negative),negativeLabels=negative,reusedGenuineStages=stages,originalFailedWitnessExit=1,originalFailedPtExit=1,originalClassesChanged=False,targetProductClassLoaded=False,targetProductMethodsExecuted=0,failedPtReexecuted=False,javaCompileOrInstrumentReexecuted=False,toolChecksOnly=True,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
