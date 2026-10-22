"""Original4203 API ClassFile pre-acquisition order; no dynamic failure or native operations."""
import hashlib
import inspect
import json
import os
import subprocess
import zipfile
import pg6820_web_prebind_original_jvm as prior
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6830_original4203_artifacts import read_whole

NAME='dev.codex.schubert.nk.api.bootstrap.ApiManagementServer'
FACTORY='Ldev/codex/schubert/nk/api/bootstrap/ApiManagementServer$Factory;'
OPEN='(Ljava/util/Map;Ljava/util/function/BooleanSupplier;I'+FACTORY+')Ldev/codex/schubert/nk/api/bootstrap/ApiManagementServer;'
CTOR='(Ljava/util/function/BooleanSupplier;Ljava/lang/String;I'+FACTORY+')V'


def definitions():
    scope={**vars(prior),'NAME':NAME,'OPEN':OPEN,'CTOR':CTOR}
    exec(compile(inspect.getsource(prior.block),'<exact API member/descriptor>','exec'),scope)
    raw=inspect.getsource(prior.inspect_order)
    for before,after in (('java/io/IOException.','java/lang/IllegalStateException.'),('WebManagementServer$Factory.create:','ApiManagementServer$Factory.create:'),("'closed'","'started'")):
        if raw.count(before)!=1:raise ValueError('one exact API ClassFile binding '+before)
        raw=raw.replace(before,after,1)
    exec(compile(raw,'<API original pre-bind order>','exec'),scope);return scope


def inspect_order(raw):return definitions()['inspect_order'](raw)


def read_original():
    qp,q,_=read_whole();jar=W/'pg6830-original4203-artifacts-v1/jars/schubert-nk-api.jar'
    if sha(jar)!=q['modules']['api']['jarSha256']:raise ValueError('original current API Jar')
    with zipfile.ZipFile(jar)as z:
        values={'api:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if values!={k:v for k,v in q['allPhysicalMainSha256'].items()if k.startswith('api:')}:raise ValueError('all original API physical bytes')
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned disassembler')
    raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',NAME],text=True)
    return qp,q,jar,raw


def main():
    qp,q,jar,raw=read_original();value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),
      jarSha256=sha(jar),classSha256=q['allPhysicalMainSha256']['api:'+NAME.replace('.','/')+'.class'],
      javapVersion='25.0.4',rawJavapSha256=hashlib.sha256(raw.encode()).hexdigest(),**inspect_order(raw),
      testsExecuted=0,additionalBuildsIssued=0,heapExhaustionExecuted=False,vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,
      toolSha256=sha(ROOT/'tools/quality/pg6842_api_prebind_original_jvm.py'))
    out=BASE/'PG6842-api-prebind-original-jvm-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),order=[value[k]for k in('diagnosticInitBci','optionalEmptyBci','bindBci','startBci')],factoryBci=value['constructorFactoryBci'])))


if __name__=='__main__':main()
