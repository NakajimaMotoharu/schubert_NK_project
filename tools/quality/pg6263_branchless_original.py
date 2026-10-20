"""Prove exactly two original delegate owners have no conditional/switch opcodes; no PT or zero injection."""
import hashlib
import json
import subprocess
from pg5940_private_lock_compile import W,TC,BASE,sha
from pg6186_native_ownership_order import methods,instructions

OWNERS=tuple('api:dev/codex/schubert/nk/api/messaging/inbound/'+n+'.class'for n in ('QuestionWorkListener','WebLogListener'))


def no_branches(blocks):
    if not blocks:raise ValueError('actual methods required')
    ops=[(name,at,op,arg)for name,body in blocks.items()for at,op,arg in instructions(body)]
    if not ops or any(op.startswith('if')or op in ('tableswitch','lookupswitch')for _,_,op,_ in ops):
        raise ValueError('actual conditional/switch means BRANCH is applicable')
    return dict(methodCount=len(blocks),instructionCount=len(ops),conditionalInstructions=[],
        methodInstructionsSha256=hashlib.sha256(json.dumps(ops,sort_keys=True).encode()).hexdigest())


def proof(source):
    qp=BASE/'PG6248-normal-phase-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6248-normal-phase-qualification-v1/manifest.safe.json'
    if sha(qp)!='4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe'or sha(private)!=q['privateManifestSha256']or q['source']!=source:
        raise ValueError('same-source actual original class map')
    p=json.loads(private.read_bytes());run=W/'pg6246-normal-phase-selected-v1/source'
    jar=run/'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    import zipfile
    with zipfile.ZipFile(jar)as z:
        actual={'api:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if actual!={k:v for k,v in p['allPhysicalMainSha256'].items()if k.startswith('api:')}:
        raise ValueError('every original API Jar class equals qualified compiled map')
    result={}
    for key in OWNERS:
        cls=key.split(':',1)[1][:-6].replace('/','.')
        raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar),cls],text=True)
        result[key]=dict(no_branches(methods(raw)),source=source,classSha256=actual[key],
            rawCounterPreserved=True,branchCounter='NOT_APPLICABLE_NO_CONDITIONAL_OR_SWITCH')
    return result


if __name__=='__main__':
    from pg6248_normal_phase_qualification import original_source
    print(json.dumps(proof(original_source()),sort_keys=True))
