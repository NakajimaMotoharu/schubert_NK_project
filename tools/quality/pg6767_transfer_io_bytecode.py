"""Original IO type bytecode applicability only; no cleanup/PT/library/VM operation."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6760_transfer_io_selected import SLOT,ADDED,guard
from pg6542_jdbc_catch_inventory import LEX,balanced

QSHA='ca1b4171ac208630189b42c6aa54f4d89b7306e29d73433c8ed55b202ba0535d'
NAMES={'Io':3,'NioIo':4}


def nested_tokens(text,name):
    seq=[(m.group(),m.start())for m in LEX.finditer(text)if not m.group().startswith(('//','/*'))]
    found=[]
    for i,(word,_)in enumerate(seq):
        if word==name and i and seq[i-1][0]in('class','record'):
            at=i+1
            while seq[at][0]!='{':at+=1
            end=balanced(seq,at,'{','}');found.append(tuple(x for x,_ in seq[i-1:end+1]))
    if len(found)!=1:raise ValueError('one unchanged nested source type '+name)
    return found[0]


def inspect_type(name,text):
    methods=len(re.findall(r'^\s+descriptor:',text,re.M))
    instructions=re.findall(r'^\s+\d+:\s+([a-z][a-z0-9_]*)',text,re.M)
    jumps=[op for op in instructions if op.startswith('if') or op in ('goto','goto_w','jsr','jsr_w','ret','tableswitch','lookupswitch')]
    if name not in NAMES or methods!=NAMES[name] or jumps:raise ValueError('exact IO method inventory and no branch/switch instruction')
    if name=='Io':
        if instructions or 'Code:' in text or text.count('public abstract ')!=3:raise ValueError('three abstract declarations, never executable coverage inferred')
    elif not instructions or text.count('Code:')!=4:
        raise ValueError('all four concrete original NioIo method bodies')
    return dict(methodDeclarations=methods,instructionCount=len(instructions),conditionalInstructions=jumps,
      applicability='DECLARATION_ONLY_NO_EXECUTABLE_CODE'if name=='Io'else'NO_CONDITIONAL_OR_SWITCH_ORIGINAL_BYTECODE',
      rawJavapSha256=hashlib.sha256(text.encode()).hexdigest())


def main():
    qp=BASE/'PG6766-transfer-io-original-v2/manifest.json';pp=W/'pg6766-transfer-io-original-v2/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze genuine current27/1669 first')
    q=json.loads(qp.read_bytes());p=json.loads(pp.read_bytes());source=q['source'];guard(source)
    if not(q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(27,10,1669) and sha(pp)==q['privateManifestSha256'] and set(q['addedPhysical'])==ADDED):raise ValueError('exact original27 all8511669 and declared additions')
    jar=W/SLOT/'source/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar)as z:
        actual={'batch:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if actual!={k:v for k,v in p['allPhysicalMainSha256'].items()if k.startswith('batch:')}:raise ValueError('every original batch class/Jar byte exact')
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned original disassembler')
    rows={}
    for name in NAMES:
        cls='dev.codex.schubert.nk.batch.file.TransferCleanup$'+name
        key='batch:'+cls.replace('.','/')+'.class'
        text=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',cls],text=True)
        row=inspect_type(name,text);counter=p['allActualCounters'].get(key)
        if name=='NioIo' and (counter is None or any(counter[k]['missed']!=0 for k in ('LINE','METHOD','CLASS')) or counter.get('BRANCH',{}).get('missed',0)!=0 or counter.get('BRANCH',{}).get('covered',0)!=0):raise ValueError('concrete NioIo actual three100 and raw branch absent/zero, never filled100')
        if name=='Io' and counter and any(x['covered']or x['missed']for x in counter.values()):raise ValueError('declaration cannot hide executable instructions')
        rows[key]=dict(**row,classSha256=actual[key],rawOriginalCounters=counter,branchCounterSynthesized=False)
    oldpub=BASE/'PG6746-request-read-original-v1/manifest.json'
    if sha(oldpub)!='af3dcb55d39916cd4883ddfa37337c92033b60080e6e9c7c44de760a35b1714a':raise ValueError('frozen old1667 original')
    oldq=json.loads(oldpub.read_bytes());oldpp=W/'pg6746-request-read-original-v1/manifest.safe.json'
    if sha(oldpp)!=oldq['privateManifestSha256']:raise ValueError('original old physical map')
    old=json.loads(oldpp.read_bytes());oldjar=W/'pg6744-request-read-selected-v1/source/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    main='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/TransferCleanup.java'
    oldtext=subprocess.check_output(['git','show',oldq['source']+':'+main],cwd=ROOT,text=True);newtext=(ROOT/main).read_text();nested={}
    with zipfile.ZipFile(oldjar)as z:
        for name in ('Counts','Outcome'):
            cls='dev.codex.schubert.nk.batch.file.TransferCleanup$'+name;key='batch:'+cls.replace('.','/')+'.class'
            if hashlib.sha256(z.read(key.split(':',1)[1])).hexdigest()!=old['allPhysicalMainSha256'][key]:raise ValueError('old nested Jar bytes exact')
            if nested_tokens(oldtext,name)!=nested_tokens(newtext,name):raise ValueError('old/new nested tokens including literals fixed')
            dumps=[subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(j),'-p','-c','-s',cls],text=True)for j in (oldjar,jar)]
            if dumps[0]!=dumps[1]:raise ValueError('full javap of unchanged nested methods/descriptor/modifiers identical')
            nested[key]=dict(beforeClassSha256=old['allPhysicalMainSha256'][key],afterClassSha256=actual[key],
              sourceTokensUnchanged=True,fullJavapEqualSha256=hashlib.sha256(dumps[0].encode()).hexdigest(),
              differenceMeaning='unchanged nested source/JVM; class metadata or debug difference, not assumed from prefix')
    value=dict(actualExit=0,source=source,originalQualificationSha256=sha(qp),originalJarSha256=sha(jar),javapVersion=version,rows=rows,nestedSourceAndJvmEquivalence=nested,
      testsExecuted=0,additionalBuildsIssued=0,vmActions=0,nativeQualified=False,formalAccepted=False,ptAlternativeCompleted=0,
      operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),toolSha256=sha(ROOT/'tools/quality/pg6767_transfer_io_bytecode.py'))
    out=BASE/'PG6767-transfer-io-bytecode-v1';os.umask(0o077);out.mkdir();path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,types=2,manifestSha256=sha(path),testsExecuted=0)))


if __name__=='__main__':main()
