"""New-only explicit independent test fixture closure; old failed build unchanged."""
import ast
import inspect
import pg1135_failed_recovery_compile as old


def source():
    raw = inspect.getsource(old)
    raw = raw.replace('pg1134-issued-api-tools-v1', 'pg1134-issued-api-tools-v2')
    raw = raw.replace('pg1135-failed-recovery-frozen-v1', 'pg1137-failed-recovery-frozen-v2')
    raw = raw.replace('PG1135-failed-recovery-compile-v1', 'PG1137-failed-recovery-compile-v2')
    raw = raw.replace("write(OUT / name, text.encode())", "write(OUT / name, text.replace('pg1134-issued-api-tools-v1','pg1134-issued-api-tools-v2').encode())")
    marker = "    java = [str(p) for p in OUT.glob('Pg1134*.java')]"
    if raw.count(marker) != 1: raise ValueError('fixed fixture closure insertion refused')
    extra = '''    for name in ['BackupPublicationFixture.java','BackupArtifactFixture.java']:
        p=ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file'/name
        write(OUT/name,p.read_bytes())
    cp+=':'+':'.join(str(repo/x)for x in ['org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar',
        'org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar','org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar'])
    java=[str(p)for p in OUT.glob('*.java')]
'''
    raw = raw.replace(marker, extra)
    raw = raw.replace("'-Werror', '-cp', cp", "'-Werror', '-sourcepath', '', '-cp', cp")
    ast.parse(raw); return raw


if __name__ == '__main__': exec(compile(source(), '<new-only closed fixture compiler>', 'exec'), {'__file__': __file__, '__name__': '__main__'})
