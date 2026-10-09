"""Compile independent same-session latest-only oracle; no business/VM operation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

T=Path(__file__).resolve().parents[4]
R=Path(__file__).resolve().parent
D=Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg746-closing-oracle-v1')


def main():
    os.umask(0o077);D.mkdir(mode=0o700);classes=D/'classes';classes.mkdir(mode=0o700)
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    dependencies=[repo/p for p in ('org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        'org/ow2/asm/asm/9.10.1/asm-9.10.1.jar','org/ow2/asm/asm-tree/9.10.1/asm-tree-9.10.1.jar',
        'org/ow2/asm/asm-commons/9.10.1/asm-commons-9.10.1.jar')]
    assert all(p.is_file() for p in dependencies)
    cp=':'.join(map(str,dependencies));jdk=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
    sources=[R/'NativeClosing746.java',R/'NativeClosing746Test.java']
    commands=[[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,sources)],
              [str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeClosing746Test']]
    outputs=[]
    with (D/'run.private.log').open('xb')as log:
        for command in commands:
            result=subprocess.run(command,capture_output=True,timeout=60)
            log.write(result.stdout+result.stderr);log.flush();os.fsync(log.fileno())
            outputs.append({'exit':result.returncode,'stdoutSha256':hashlib.sha256(result.stdout).hexdigest(),'stderrBytes':len(result.stderr)})
            assert result.returncode==0 and not result.stderr
    record={'actualExit':0,'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
            'commands':commands,'results':outputs,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources+dependencies+list(classes.glob('*.class'))},
            'latestOnly':True,'monotonicProbeOracle':True,'actualNativeQualified':False,'formalAccepted':False}
    with (D/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'compileWerror':True,'literalLatestOnlyOracle':True,'actualNativeQualified':False,
                     'manifestSha256':hashlib.sha256((D/'manifest.safe.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
