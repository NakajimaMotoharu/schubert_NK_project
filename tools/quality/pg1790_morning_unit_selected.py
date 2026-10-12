"""Independent Unit-only JUnit fixture, no Production compile/VM or DB action."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from pg1625_unsupported_ports_selected import LIBRARIES

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
TC=Path('/home/mini/codex/project1/work/toolchain')
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceUnitTest.java',
       'src/deployment/systemd/schubert-nk-morning-controller.service.template',
       'tools/quality/vm/050_s1/Pg1790MorningUnitLauncher.java']


def main():
    if sys.argv[1:]not in (['red'],['green']):raise ValueError('exact red/green new-only fixture')
    phase=sys.argv[1];os.umask(0o077);out=W/('pg1790-morning-unit-'+phase+'-v1');out.mkdir(mode=0o700)
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in FILES}
    libraries={n:hashlib.sha256((TC/'m2/repository'/n).read_bytes()).hexdigest()for n in LIBRARIES}
    classes=out/'classes';classes.mkdir();jdk=TC/'jdk-25.0.4/bin'
    cp=':'.join(str(TC/'m2/repository'/n)for n in LIBRARIES)
    commands=[]
    def execute(label,args):
        start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        r=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,timeout=60)
        (out/(label+'.private.log')).write_bytes(r.stdout+r.stderr)
        commands.append({'label':label,'argv':args,'exit':r.returncode,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'logSha256':hashlib.sha256(r.stdout+r.stderr).hexdigest()})
        return r.returncode
    javac=execute('javac',[str(jdk/'javac'),'-Werror','-Xlint:all','-cp',cp,'-d',str(classes),str(ROOT/FILES[0]),str(ROOT/FILES[2])])
    if javac!=0:raise ValueError('Unit fixture compile failed before tests')
    xml=out/'TEST-MorningServiceUnitTest.xml'
    actual=execute('junit',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'Pg1790MorningUnitLauncher',str(ROOT),str(xml)])
    x=ET.parse(xml).getroot();cases=x.findall('testcase')
    if x.attrib['tests']!='4'or len(cases)!=4 or x.attrib['errors']!='0'or x.attrib['skipped']!='0'or len({c.attrib['name']for c in cases})!=4:raise ValueError('all four actual unique tests required')
    if phase=='red'and(actual!=1 or x.attrib['failures']!='1'):raise ValueError('existing missing WARNING contract must fail exactly one test')
    if phase=='green'and(actual!=0 or x.attrib['failures']!='0'):raise ValueError('all four tests must pass')
    if hashes!={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in FILES}:raise ValueError('fixture bytes changed')
    result={'actualExit':actual,'phase':phase,'testSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'inputHashes':hashes,'libraries':libraries,'tests':4,'failures':int(x.attrib['failures']),'errors':0,'skipped':0,'javacWarnings':0,'commands':commands,'xmlSha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'vmDbMutations0':True,'formalAccepted':False,'wholeRegressionNotRun':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'phase':phase,'actualExit':actual,'tests':4,'failures':result['failures'],'xmlSha256':result['xmlSha256'],'vmDbMutations0':True,'formalAccepted':False}))
    return 0


if __name__=='__main__':raise SystemExit(main())
