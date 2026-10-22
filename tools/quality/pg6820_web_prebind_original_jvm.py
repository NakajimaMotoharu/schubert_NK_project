"""SS312 original ClassFile acquisition/cleanup preparation order; static only, never heap exhaustion."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6804_original4202_artifacts import read_whole

NAME='dev.codex.schubert.nk.web.bootstrap.WebManagementServer'
FACTORY='Ldev/codex/schubert/nk/web/bootstrap/WebManagementServer$Factory;'
OPEN='(Ljava/util/Map;Ljava/util/function/BooleanSupplier;I'+FACTORY+')Ldev/codex/schubert/nk/web/bootstrap/WebManagementServer;'
CTOR='(Ljava/util/function/BooleanSupplier;Ljava/lang/String;I'+FACTORY+')V'


def block(raw,descriptor):
    member={OPEN:'open',CTOR:NAME}.get(descriptor)
    if member is None:raise ValueError('one of two explicit method identities')
    chunks=re.split(r'(?=^  (?:public|protected|private|static)\b[^\n]*[;{]$)',raw,flags=re.M)
    found=[s for s in chunks if '    descriptor: '+descriptor+'\n'in s and re.search(r'\b'+re.escape(member)+r'\(',s.splitlines()[0])]
    if len(found)!=1:raise ValueError('one exact original JVM descriptor')
    return found[0]


def inspect_order(raw):
    opened=block(raw,OPEN);ctor=block(raw,CTOR)
    def calls(text):
        return [(int(at),op,target)for at,op,target in re.findall(r'^\s+(\d+): (invoke\w+)\s+[^\n]*// (?:Method|InterfaceMethod) ([^\n]+)$',text,re.M)]
    def one(rows,needle):
        found=[at for at,_,target in rows if needle in target]
        if len(found)!=1:raise ValueError('one original JVM invocation '+needle)
        return found[0]
    opencalls=calls(opened)
    diagnostic=one(opencalls,'java/io/IOException."<init>"')
    empty=one(opencalls,'java/util/Optional.empty:')
    binding=one(opencalls,'bind:')
    starting=one(opencalls,'start:')
    if not diagnostic<empty<binding<starting:raise ValueError('diagnostic and typed empty must precede bind, then start')
    factory=one(calls(ctor),'WebManagementServer$Factory.create:')
    puts=[(int(at),name)for at,name in re.findall(r'^\s+(\d+): putfield\s+[^\n]*// Field ([^:\s]+):',ctor,re.M)]
    needed={'promoted','promotionAttempted','closed','stopping','stopLock','healthy','information','executor'}
    if not needed<={name for at,name in puts if at<factory}or [name for at,name in puts if at>factory]!=['server']:
        raise ValueError('all acquired-owner fields before factory, only final server stored after')
    allocations=[(int(at),op)for at,op in re.findall(r'^\s+(\d+): (new|newarray|anewarray|multianewarray|invokedynamic)\b',ctor,re.M)]
    if any(at>factory for at,_ in allocations):raise ValueError('no unprotected post-factory allocation')
    tail=[(at,op,target)for at,op,target in calls(ctor)if at>factory]
    if len(tail)!=1 or 'java/util/Objects.requireNonNull:'not in tail[0][2]:raise ValueError('post-factory only fixed null rejection before final store')
    return dict(diagnosticInitBci=diagnostic,optionalEmptyBci=empty,bindBci=binding,startBci=starting,
      constructorFactoryBci=factory,preparedFields=sorted(needed),postFactoryStoredFields=['server'],postFactoryAllocations=[],
      openMethodSha256=hashlib.sha256(opened.encode()).hexdigest(),constructorMethodSha256=hashlib.sha256(ctor.encode()).hexdigest())


def read_original():
    qp,q,_=read_whole();jar=W/'pg6804-original4202-artifacts-v1/jars/schubert-nk-web.jar'
    if sha(jar)!=q['modules']['web']['jarSha256']:raise ValueError('original current full Web Jar')
    with zipfile.ZipFile(jar)as z:
        values={'web:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if values!={k:v for k,v in q['allPhysicalMainSha256'].items()if k.startswith('web:')}:raise ValueError('all original Web physical bytes')
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned static disassembler')
    raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',NAME],text=True)
    return qp,q,jar,raw


def main():
    qp,q,jar,raw=read_original();value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),
      jarSha256=sha(jar),classSha256=q['allPhysicalMainSha256']['web:'+NAME.replace('.','/')+'.class'],
      javapVersion='25.0.4',rawJavapSha256=hashlib.sha256(raw.encode()).hexdigest(),**inspect_order(raw),
      testsExecuted=0,additionalBuildsIssued=0,heapExhaustionExecuted=False,vmActions=0,
      formalAccepted=False,ptAlternativeCompleted=0,toolSha256=sha(ROOT/'tools/quality/pg6820_web_prebind_original_jvm.py'))
    out=BASE/'PG6820-web-prebind-original-jvm-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),order=[value[k]for k in('diagnosticInitBci','optionalEmptyBci','bindBci','startBci')],factoryBci=value['constructorFactoryBci'])))


if __name__=='__main__':main()
