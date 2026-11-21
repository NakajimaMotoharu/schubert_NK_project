"""Strict JaCoCo class identity guard with independent literal metadata vectors."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT=Path.cwd()
OPS=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence'
TOOLS=ROOT/'tools/quality'
TC=ROOT.parent/'toolchain'
JDK=TC/'jdk-25.0.4/bin'
CACHE=TC/'m2/repository'
JAVA=TOOLS/'jacoco/UnfilteredCodeMeasurement.java'
DECODER=TOOLS/'jacoco_readonly_exec_subset.py'
HEADER=bytes.fromhex('01c0c01007')
SESSION=bytes.fromhex('10 0003 52554e 0000000000000001 0000000000000002')
VALID_NAME=bytes.fromhex('11 0000000000000001 0001 58 03 05')
EMPTY_NAME=bytes.fromhex('11 0000000000000004 0000 01 01')
DEP=[CACHE/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*(
    CACHE/f'org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-commons','asm-tree'))]

def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())

def main(green):
    source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    started=next((ROOT/'documents/400_PGPT/470_PMO').glob('601_*/1780_*.json'))
    base=json.loads(started.read_bytes())['values']['source']
    diff=subprocess.check_output(['git','diff','--name-only',base,source,'--',JAVA,DECODER],text=True).splitlines()
    assert set(diff)==({str(JAVA.relative_to(ROOT)),str(DECODER.relative_to(ROOT))} if green else set())
    name='PG41418-strict-exec-empty-class-green-v2' if green else 'PG41414-strict-exec-empty-class-red-v1'
    out=OPS/name
    out.mkdir()
    steps={}
    env=dict(os.environ,PYTHONPATH=str(TOOLS),PYTHONDONTWRITEBYTECODE='1')
    def run(label,argv,expected):
        cmd=list(map(str,argv))
        proc=subprocess.run(cmd,env=env,capture_output=True,timeout=90,check=False)
        stdout,stderr=out/(label+'.stdout.txt'),out/(label+'.stderr.txt')
        stdout.write_bytes(proc.stdout)
        stderr.write_bytes(proc.stderr)
        steps[label]=dict(argv=cmd,actualExit=proc.returncode,stdout=pin(stdout),stderr=pin(stderr))
        assert proc.returncode==expected,(label,proc.returncode,proc.stderr.decode()[-300:])
        return proc.stdout.decode(),proc.stderr.decode()
    if green:
        suite=[str(p.relative_to(TOOLS).with_suffix('')) for p in sorted(TOOLS.glob('jacoco_readonly_exec_subset*_test.py'))]
        suite.append('public_jacoco_exec_format_utf_test')
        _,stderr=run('python',[sys.executable,'-B','-m','unittest',*suite],0)
        assert '\nOK\n' in stderr
        selftest, _=run('historical-12',[sys.executable,'-B','-c',
            'from jacoco_readonly_exec_subset import selftest; print(selftest())'],0)
        assert selftest.strip()=='12'
    else:
        _,stderr=run('python',[sys.executable,'-B','-m','unittest',
            'jacoco_readonly_exec_subset_scope_test.ClassSelectionScopeTest.test_empty_record_name_is_invalid_even_when_not_selected'],1)
        assert stderr.count('ValueError not raised')==2
    formula='org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement'
    read_only_classes=0
    prior_changed_product_run=next(OPS.glob('PG41410*/manifest.json'))
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-empty-class-record-') as slot:
        work=Path(slot)
        lib=os.pathsep.join(map(str,DEP))
        fixture_source=work/'Plain.java'
        fixture_source.write_text('package fixture; public final class Plain { public int value() { return 5; } }\n')
        directory=work/'classes'
        compile=[JDK/'javac','--release','25','-Xlint:all','-Werror','-proc:none']
        run('compile-fixture',[*compile,'-d',directory,fixture_source],0)
        run('compile-reader',[*compile,'-cp',lib,'-d',work/'tool',JAVA],0)
        java=[JDK/'java','-cp',str(work/'tool')+os.pathsep+lib,formula,'--strict-original-exec']
        fixture=directory/'fixture/Plain.class'
        valid=work/'valid.exec'
        invalid=work/'invalid.exec'
        valid.write_bytes(HEADER+SESSION+VALID_NAME)
        invalid.write_bytes(HEADER+SESSION+VALID_NAME+EMPTY_NAME)
        result,_=run('java-valid',[*java,valid,fixture],0)
        assert result.startswith('CLASS\tfixture/Plain\t')
        result,err=run('java-empty',[*java,invalid,fixture],1 if green else 0)
        assert (not result and 'nonempty original class name required' in err) if green else result.startswith('CLASS\tfixture/Plain\t')
        if green:
            fallback,_=run('java-writer-compat',[*java[:-1],invalid,fixture],0)
            assert fallback.startswith('CLASS\tfixture/Plain\t')
            real=json.loads(prior_changed_product_run.read_bytes())
            assert real['driverClasspathEntries']==real['actualDbOps']==real['heldClassesOpened']==0
            current=Path(real['originalExec']['path'])
            assert pin(current)==real['originalExec']
            classes=[Path(x['path']) for x in real['currentClassFiles']]
            assert all(pin(p)==x for p,x in zip(classes,real['currentClassFiles'],strict=True)) and len(classes)==10
            expected=[x for x in classes if x.name=='JdbcOutboxRepository.class']
            assert len(expected)==1
            proof,_=run('original-jdbc-readonly',[*java,current,*expected],0)
            assert proof.startswith('CLASS\tdev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository\t')
            run('original-python-readonly',[sys.executable,'-B','-c',
                'from pathlib import Path; import sys; from jacoco_readonly_exec_subset import decode; '
                'assert len(decode(Path(sys.argv[1]).read_bytes(),{sys.argv[2]},strict_class_names=True)["classes"])==1',
                current,'dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository'],0)
            read_only_classes=len(expected)
    report=dict(run=name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=source,
        inputFixtureSha256=sha256(HEADER+SESSION+VALID_NAME+EMPTY_NAME).hexdigest(),beforeSource=base,
        javacStrict=0,scope='strict original exec record with empty name',baselineAcceptedBoth=not green,
        javaEmptyNameActualExit=1 if green else 0,pythonNegativeVectors=2,javaNegativeVectors=1,
        toolTestDefinitions=1,knownOrdinaryExistingOriginalReads=read_only_classes,
        priorCurrentUnit=pin(prior_changed_product_run),runtimeNativeOperations=0,productTestsExecuted=0,formalDelta=0,steps=steps)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(name,read_only_classes,report['javaEmptyNameActualExit'])

if __name__=='__main__':
    main(sys.argv[1]=='green')
