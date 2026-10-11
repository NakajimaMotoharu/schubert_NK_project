"""Freeze/package package-only typed SSC266 helper; independent realFD tests, no VM action."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1485_inspector_closing_qualification import SOURCE,W,require,sha

ROOT=Path(__file__).resolve().parents[2]

def main():
    os.umask(0o077);require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out=W/'pg1488-publication-helper-frozen-v1';out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir(mode=0o700)
    release=W/'pg1292-release-v1';cp=':'.join(str(p)for p in [release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*'])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    annotations=['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar','org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar','org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar','org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar']
    for name in annotations:require((repo/name).is_file())
    cp+=':'+':'.join(str(repo/name)for name in annotations)
    j=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin');tools=ROOT/'tools/quality/vm/050_s1'
    sources=[tools/'Pg1487PublicationOnlyIntent.java',tools/'Pg1487PublicationOnlyIntentTest.java']
    testsource=ROOT/'src/schubert-nk-batch/src/test/java'
    before={str(p.relative_to(ROOT)):sha(p)for p in sources}
    start=datetime.datetime.now(datetime.timezone.utc);phases=[]
    for index,args in enumerate([
      [str(j/'javac'),'-Xlint:all','-Werror','-cp',cp,'-sourcepath',str(testsource),'-d',str(classes),*map(str,sources)],
      [str(j/'java'),'--enable-native-access=ALL-UNNAMED','-cp',str(classes)+':'+cp,'dev.codex.schubert.nk.batch.file.Pg1487PublicationOnlyIntentTest']]):
        p=out/('phase-'+str(index)+'.private.log')
        with p.open('xb')as f:r=subprocess.run(args,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'exit':r.returncode,'logSha256':sha(p)})
        if r.returncode:break
    require(head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    require(before=={str(p.relative_to(ROOT)):sha(p)for p in sources})
    # Only two known operator classes enter the deployable flat JAR. Test fixtures never deploy.
    jar=out/'publication-only-helper.jar';package='dev/codex/schubert/nk/batch/file/'
    if phases[-1]['exit']==0:
        args=[str(j/'jar'),'--create','--file',str(jar),'--date=2026-10-12T00:00:00Z']
        for name in ('Pg1487PublicationOnlyIntent.class','Pg1487PublicationOnlyIntent$Gate.class'):args+=['-C',str(classes),package+name]
        with(out/'package.private.log').open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f)
        phases.append({'exit':r.returncode,'logSha256':sha(out/'package.private.log')})
    manifest={'run':'PG1488-publication-helper-frozen-v1','actualExit':phases[-1]['exit'],'operatorSource':head,'productionSource':SOURCE,'startUTC':start.isoformat(),'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceHashes':before,'phases':phases,'jarSha256':sha(jar)if jar.exists()else None,'vmActions0':True,'formalAccepted':False,'productionPtDelta':0,'nativeAcceptancePending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest));return manifest['actualExit']

if __name__=='__main__':raise SystemExit(main())
