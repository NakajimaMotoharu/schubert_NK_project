"""Read-only protocol dependency qualification, no Java target initialization or M2 overwrite."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import zipfile
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7625-api-inbox-protocol-preflight-v1'
WITNESS=host.BASE/'PG7614-dlq-health-six-compile-v1/manifest.json'
WITNESS_SHA='ab68b2c6f3118b6d38d234b6d0820a908b20f4ca8fef9083d2b0ddc057e729f2'
SOURCE='cfd8c12ddfeb6be74b41029478c4df76b124ccfe'
LOCAL=host.TC/'m2/repository/dev/codex/schubert/schubert-nk-protocol/0.1.0-SNAPSHOT/schubert-nk-protocol-0.1.0-SNAPSHOT.jar'

def require(value,message):
    if not value:raise ValueError(message)

def classes(path):
    require(path.is_file() and path.stat().st_size<10_000_000,'bounded actual owned dependency Jar')
    with zipfile.ZipFile(path) as archive:
        names=[p for p in archive.namelist() if p.endswith('.class')]
        require(len(names)==len(set(names)),'no duplicate class entry')
        return {p:hashlib.sha256(archive.read(p)).hexdigest() for p in names}

def validate(witness,selected,selected_hash,actual_inputs,current_inputs):
    require(witness['source']==SOURCE and witness['actualExit']==witness['terminal']['actualExit']==0
      and witness['testsExecuted']==0 and witness['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY',
      'exact completed normal compile, never a business PT PASS')
    require(selected_hash==witness['jars']['protocol']['sha256'] and len(selected)==176,
      'only exact qualified normal Jar, no stale M2 substitution')
    require(actual_inputs==current_inputs and actual_inputs,'all original protocol inputs unchanged, no source transfer')

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only preflight')
    require(host.sha(WITNESS)==WITNESS_SHA,'exact original normal witness')
    normal=json.loads(WITNESS.read_bytes());jar=Path(normal['jars']['protocol']['path'])
    selected=classes(jar);local=classes(LOCAL);local_sha=host.sha(LOCAL)
    inputs={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/schubert-nk-protocol/')}
    current={p:host.sha(host.ROOT/p) for p in inputs}
    validate(normal,selected,host.sha(jar),inputs,current)
    # Bind every actual class independently to the completed six-Jar physical proof.
    physical_file=host.BASE/'PG7616-dlq-health-six-post-v1/manifest.json'
    require(host.sha(physical_file)=='fd65a13a29b1a4b1f6a82541e66b9fde5259e7f39830dfbf19b8f993fbe8b4c7','actual six physical witness')
    physical=json.loads(physical_file.read_bytes())
    with zipfile.ZipFile(jar) as archive:
        require({p:hashlib.sha256(archive.read(p)).hexdigest() for p in selected}==selected,'every frozen entry re-read')
    # Six-post already proved equality to original1669 plus explicit monitoring deltas; its Jar pin
    # is rechecked rather than trusting a count or a self-declared source name.
    require(physical['source']==SOURCE and physical['actualExit']==0
      and physical['jars']['protocol']==normal['jars']['protocol'] and physical['oldPhysicalUnchanged']==1669,
      'original protocol bytes/debug unchanged through genuine physical proof')
    negative=[]
    for kind in ('stale-m2','wrong-source','unknown-terminal','changed-input','wrong-selected-hash'):
        changed=copy.deepcopy(normal);candidate=selected;sha=host.sha(jar);actual=dict(inputs)
        if kind=='stale-m2':candidate=local;sha=local_sha
        elif kind=='wrong-source':changed['source']='0'*40
        elif kind=='unknown-terminal':changed['terminal']['actualExit']=None
        elif kind=='changed-input':actual[next(iter(actual))]='0'*64
        else:sha='0'*64
        try:validate(changed,candidate,sha,actual,current)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('dependency/source/terminal mutation accepted')
    prefix='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/'
    closure={prefix+p:current[prefix+p] for p in (
      'layout/LayoutRegistry.java','layout/LayoutDefinition.java','layout/LayoutId.java',
      'layout/LayoutValidationException.java','layout/UnsupportedLayoutException.java',
      'header/ResultCode.java','header/MessageKind.java','header/InteractionKind.java')}
    require(host.sha(LOCAL)==local_sha,'existing M2 Jar retained unchanged, never overwritten')
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,
      source=SOURCE,normalWitness=dict(path=str(WITNESS),sha256=WITNESS_SHA),selectedProtocolJar=dict(path=str(jar),sha256=host.sha(jar),classCount=len(selected)),
      allSelectedClassSha256=selected,protocolSourceInputs=current,pureInitializerClosure=closure,
      initializerReview='LayoutRegistry -> immutable standard64 metadata + LayoutDefinition/Id/JDK validation and three literal enums; exceptions only super/serial UID; no file/network/DB/key/Root/provider operation',
      m2Retained=dict(path=str(LOCAL),sha256=local_sha,classCount=len(local),qualified=False,used=False,
        missing=len(set(selected)-set(local)),extra=len(set(local)-set(selected)),different=sum(selected[k]!=local[k] for k in set(selected)&set(local))),
      negativeGuards=negative,targetInitialization=False,javaExecuted=False,ptExecuted=0,vmActions=0,databaseActions=0,
      dependenciesCopiedToGit=False,m2Overwritten=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,normalClasses=len(selected),staleM2Classes=len(local),staleM2Used=False,negativeGuards=len(negative),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
