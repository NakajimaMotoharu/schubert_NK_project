"""Exact ordinary callback expansion proof, not a Production test oracle or native admission."""
import hashlib
import json
import os
import subprocess
from pg5940_private_lock_compile import ROOT,W,sha
from pg6542_jdbc_catch_inventory import LEX

OLD='d48f8ebf8ed4047763c77fe487c44f7caa03e8f8'
FIELD='ORDINARY_UNCONFIRMED'
PATHS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ArtemisConnectionFactoryProvider.java':2,
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java':4}


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def expand_to_original(before,after,count):
    old=tokens(before);new=tokens(after)
    declaration=tokens('private static final Consumer<Throwable> '+FIELD+' = ignored -> {};')
    positions=[i for i in range(len(new)) if new[i:i+len(declaration)]==declaration]
    if len(positions)!=1:raise ValueError('one exact private static final stateless observer')
    at=positions[0];rest=new[:at]+new[at+len(declaration):]
    if rest.count(FIELD)!=count:raise ValueError('exact old ordinary callsite count')
    expanded=[]
    for word in rest:
        expanded.extend(tokens('ignored -> {}') if word==FIELD else [word])
    if expanded!=old:raise ValueError('all literal/native-choice/ownership tokens unchanged after expansion')
    return dict(expandedTokensSha256=hashlib.sha256(json.dumps(old,separators=(',',':')).encode()).hexdigest(),
                ordinaryCallsites=count,sharedDefinitions=1,nativeChoiceUnchanged=True)


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('clean committed source before publishing equivalence')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=set(PATHS) or subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('only two Main; all old Test/build/Current/static fixed')
    rows=[]
    for path,count in PATHS.items():
        before=subprocess.check_output(['git','show',OLD+':'+path],cwd=ROOT,text=True)
        rows.append(dict(path=path,oldSha256=hashlib.sha256(before.encode()).hexdigest(),
          sourceSha256=sha(ROOT/path),**expand_to_original(before,(ROOT/path).read_text(),count)))
    out=W/'pg6722-observer-expansion-proof-v1';os.umask(0o077);out.mkdir()
    value=dict(actualExit=0,source=source,priorSource=OLD,rows=rows,
      classification='SOURCE_EQUIVALENCE_NOT_TEST_ORACLE',testsExecuted=0,nativeQualified=False,
      vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,toolSha256=sha(ROOT/'tools/quality/pg6722_broker_noop_equivalence.py'))
    target=out/'manifest.safe.json'
    with target.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,paths=2,oldCallsites=6,sharedDefinitions=2,manifestSha256=sha(target))))


if __name__=='__main__':main()
