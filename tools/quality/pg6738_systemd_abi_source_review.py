"""Read-only PG comparison against independent ABI shapes; no native call/library/process IO."""
import hashlib
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6542_jdbc_catch_inventory import LEX,balanced

SOURCE='01e41088c6562c3b7d103ae0bacc9f693bc1aad4'
MAIN='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java'
SPEC='evidence/01_PT/018_NK-OPS-001/1476_SystemdBinderABI_後続独立fixture仕様.md'
LAYOUTS={'ADDRESS':'P','JAVA_INT':'I','JAVA_LONG':'L','JAVA_BYTE':'B'}


def expected_table(text):
    rows=re.findall(r'^\|([a-z][a-z_]+)\|([PILBV]:[PILB]*)\|$',text,re.M)
    result=dict(rows)
    if len(rows)!=21 or len(result)!=21:raise ValueError('21 unique independent ABI shapes')
    return result


def actual_table(text):
    tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    matches=[]
    for i,(word,_) in enumerate(tokens):
        if word=='bind' and i and tokens[i-1][0]=='Calls' and tokens[i+1][0]=='(':
            last=balanced(tokens,i+1,'(',')');body=last+1
            while tokens[body][0]!='{':body+=1
            end=balanced(tokens,body,'{','}');matches.append((tokens[body][1],tokens[end][1]+1))
    if len(matches)!=1:raise ValueError('one explicit Calls bind body')
    body=text[slice(*matches[0])]
    aliases={name:LAYOUTS[kind] for name,kind in re.findall(r'var\s+(\w+)\s*=\s*ValueLayout\.(\w+)\s*;',body) if kind in LAYOUTS}
    if len(aliases)!=4:raise ValueError('four reviewed actual ValueLayout aliases')
    constants=dict(re.findall(r'\b(\w+)\s*=\s*"([^"\n]+)"\s*;',text))
    rows=re.findall(r'Map\.entry\(\s*("[^"\n]+"|\w+)\s*,\s*FunctionDescriptor\.(ofVoid|of)\(([^)]*)\)\s*\)',body,re.S)
    actual={}
    for key,kind,arguments in rows:
        name=key[1:-1] if key.startswith('"') else constants.get(key)
        if name is None or name in actual:raise ValueError('unique explicit closed-symbol key')
        words=[x.strip() for x in arguments.split(',')]
        if any(x not in aliases for x in words):raise ValueError('only explicit scalar/pointer aliases')
        layouts=[aliases[x] for x in words]
        actual[name]=('V:'+''.join(layouts)) if kind=='ofVoid' else layouts[0]+':'+''.join(layouts[1:])
    if len(rows)!=21 or len(actual)!=21:raise ValueError('all21 actual descriptors, no silent parser omission')
    words=[m.group() for m in LEX.finditer(body) if not m.group().startswith(('//','/*'))]
    routing=[m.group() for m in LEX.finditer('SymbolLookup lookup = entry.getKey().equals("free") ? libc : systemd;')]
    if sum(words[i:i+len(routing)]==routing for i in range(len(words)))!=1:
        raise ValueError('one explicit libc free / systemd other resolution')
    return actual


def verify(before,oracle):
    expected=expected_table(oracle);actual=actual_table(before)
    if actual!=expected:raise ValueError('actual ABI differs from independent fixed header shapes')
    return actual


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('current Main/Test/gates fixed while original whole runs')
    text=(ROOT/MAIN).read_text();oracle=(ROOT/SPEC).read_text();actual=verify(text,oracle)
    old=subprocess.check_output(['git','show',SOURCE+':'+MAIN],cwd=ROOT)
    if hashlib.sha256(old).hexdigest()!=sha(ROOT/MAIN):raise ValueError('exact Production source reviewed')
    out=BASE/'PG6738-systemd-abi-source-review-v1';os.umask(0o077);out.mkdir()
    value=dict(actualExit=0,productionSource=SOURCE,sourcePath=MAIN,sourceSha256=sha(ROOT/MAIN),
      independentSpecPath=SPEC,independentSpecSha256=sha(ROOT/SPEC),shapes=actual,symbols=21,
      reviewKind='PG_SOURCE_REVIEW_NOT_DYNAMIC_NATIVE_QUALIFICATION',implementationChangeNeeded=False,
      testsExecuted=0,nativeCalls=0,libraryLoads=0,vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,
      runtimeOwnershipProved=False,toolSha256=sha(ROOT/'tools/quality/pg6738_systemd_abi_source_review.py'),
      operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    path=out/'manifest.json'
    with path.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,symbols=21,implementationChangeNeeded=False,testsExecuted=0,manifestSha256=sha(path))))


if __name__=='__main__':main()
