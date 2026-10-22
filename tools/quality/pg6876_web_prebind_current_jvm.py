"""Original4209 Web ClassFile acquisition order, static only; no heap failure or native action."""
import hashlib
import json
import os
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6864_original4209_artifacts import read_whole
from pg6820_web_prebind_original_jvm import NAME,inspect_order


def read_original():
    qp,q,_=read_whole();jar=W/'pg6864-original4209-artifacts-v1/jars/schubert-nk-web.jar'
    if sha(jar)!=q['modules']['web']['jarSha256']:raise ValueError('actual original Web Jar')
    with zipfile.ZipFile(jar)as z:
        values={'web:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if values!={k:v for k,v in q['allPhysicalMainSha256'].items()if k.startswith('web:')}:raise ValueError('all actual original Web physical bytes')
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned disassembler')
    raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-s',NAME],text=True)
    return qp,q,jar,raw


def main():
    qp,q,jar,raw=read_original();value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),
      jarSha256=sha(jar),classSha256=q['allPhysicalMainSha256']['web:'+NAME.replace('.','/')+'.class'],
      javapVersion='25.0.4',rawJavapSha256=hashlib.sha256(raw.encode()).hexdigest(),**inspect_order(raw),
      testsExecuted=0,additionalBuildsIssued=0,heapExhaustionExecuted=False,vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,
      toolSha256=sha(ROOT/'tools/quality/pg6876_web_prebind_current_jvm.py'))
    out=BASE/'PG6876-web-prebind-current-jvm-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),order=[value[k]for k in('diagnosticInitBci','optionalEmptyBci','bindBci','startBci')],factoryBci=value['constructorFactoryBci'])))


if __name__=='__main__':main()
