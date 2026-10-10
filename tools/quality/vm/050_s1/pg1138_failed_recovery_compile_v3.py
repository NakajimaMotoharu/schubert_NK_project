"""New-only transitive independent fixture closure; v1/v2 failures preserved."""
import ast
from pg1137_failed_recovery_compile_v2 import source as previous


def source():
    raw = previous()
    raw = raw.replace('pg1134-issued-api-tools-v2', 'pg1134-issued-api-tools-v3')
    raw = raw.replace('pg1137-failed-recovery-frozen-v2', 'pg1138-failed-recovery-frozen-v3')
    raw = raw.replace('PG1137-failed-recovery-compile-v2', 'PG1138-failed-recovery-compile-v3')
    marker = "    java=[str(p)for p in OUT.glob('*.java')]"
    if raw.count(marker) != 1: raise ValueError('fixed transitive fixture insertion refused')
    raw = raw.replace(marker, "    write(OUT/'BackupManifestFixture.java',(ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java').read_bytes())\n" + marker)
    raw = raw.replace("'pg113[34]*test.py'", "'pg113[3478]*test.py'")
    raw = raw.replace("print(json.dumps({k: v for k, v in result.items() if k != 'fileHashes'}))",
                      "print(json.dumps({**{k:v for k,v in result.items()if k not in ['fileHashes','phases']},'phases':[{k:v for k,v in p.items()if k!='command'}for p in result['phases']]}))")
    ast.parse(raw); return raw


if __name__ == '__main__': exec(compile(source(), '<new-only transitive fixture compiler>', 'exec'), {'__file__': __file__, '__name__': '__main__'})
