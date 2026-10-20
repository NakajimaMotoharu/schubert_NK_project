"""Inspect original old/new Jar methods only; no build,JUnit,DB or native invocation."""
import hashlib
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6054_expiry_read_qualification import SOURCE
from pg6008_api_bounds_static import executable_sections


def methods(text):
    chunks = re.split(r'(?m)(?=^  \S)', executable_sections(text))
    result = {p.splitlines()[0]: p.strip() for p in chunks if p.strip()}
    if len(result) != len([p for p in chunks if p.strip()]):
        raise ValueError('unique executable signature blocks')
    return result


def intended_change(before, after):
    added = set(after)-set(before)
    changed = {k for k in before.keys() & after.keys() if before[k] != after[k]}
    read = '  public java.util.Optional<dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository$Snapshot> read(dev.codex.schubert.nk.batch.repository.BatchStepAttempt);'
    helper = '  private static <T> T presentRead(T) throws java.sql.SQLDataException;'
    if set(before)-set(after) or added != {helper} or changed != {read}:
        raise ValueError('only exact read method change plus private presentRead helper')
    return added, changed


def main():
    q = BASE/'PG6054-expiry-read-qualification-v1/manifest.json'
    if sha(q) != '9f1269de6b66c0be2467aab5de164e82553f03d33dc79f5212e410ff4f1daee9':
        raise ValueError('actual148/8511667/4 physical differences')
    qualified = json.loads(q.read_bytes())
    if qualified['source'] != SOURCE:
        raise ValueError('exact current Main source')
    old = W/'pg6042-original3976-artifacts-v2/jars/schubert-nk-batch.jar'
    new = W/'pg6052-expiry-combined-green-v1/source/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    cls = 'dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository'
    def read(path, name, flags):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *flags, '-classpath', str(path), name], text=True)
    before = methods(read(old, cls, ['-p', '-c', '-s'])); after = methods(read(new, cls, ['-p', '-c', '-s']))
    added, changed = intended_change(before, after)
    abi = read(new, cls, ['-public', '-s'])
    if abi != read(old, cls, ['-public', '-s']):
        raise ValueError('public ABI unchanged')
    nested = [k.split(':', 1)[1][:-6].replace('/', '.') for k in qualified['changedPhysical'] if '$' in k]
    if len(nested) != 3 or any(methods(read(old, n, ['-p', '-c', '-s'])) != methods(read(new, n, ['-p', '-c', '-s'])) for n in nested):
        raise ValueError('three actual nested differences debug-only;all methods unchanged')
    result = dict(actualExit=0, source=SOURCE, referenceSha256=sha(q), oldJarSha256=sha(old), newJarSha256=sha(new),
        addedPrivateMethods=sorted(added), changedExistingMethods=sorted(changed), unchangedExistingMethods=len(before)-len(changed),
        publicAbiUnchanged=True, publicAbiSha256=hashlib.sha256(abi.encode()).hexdigest(),
        nestedDebugOnly=sorted(nested), additionalBuildsIssued=0, testsExecuted=0, vmActions=0, formalAccepted=False)
    os.umask(0o077); out = BASE/'PG6056-expiry-read-methods-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(result | dict(manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
