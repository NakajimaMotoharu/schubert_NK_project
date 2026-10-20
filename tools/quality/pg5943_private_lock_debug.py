"""Read/disassemble20 nonexecutably changed nested/outer classes; no PT or Main calls."""
import json
import os
import subprocess
from pg5940_private_lock_compile import TC, BASE, W, MODULES, plan, sha


def main():
    sp = BASE/'PG5942-private-lock-static-v1/manifest.json'
    if sha(sp) != 'fba315bab4168d6150638c7a21b5209dfce88b0f97951e456ed3d52d33edbda5':
        raise ValueError('actual33source/54 physical/34 required current static')
    value = json.loads(sp.read_bytes()); required = set(plan()['requiredClassKeys'])
    others = set(value['changedPhysicalClasses'])-required
    if len(others) != 20 or len(required) != 34:
        raise ValueError('all54 differences partitioned, never subtract unknown classes')
    old = W/'pg5912-api-expression-selected35-v1/source'; new = W/'pg5940-private-lock-compile-v1/source'
    result = []
    for module in MODULES:
        keys = sorted(k for k in others if k.startswith(module+':'))
        if not keys:
            continue
        names = [k.split(':', 1)[1][:-6].replace('/', '.') for k in keys]
        def bytecode(root):
            return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-c', '-p', '-s', '-classpath', str(root/('src/schubert-nk-'+module+'/target/classes')), *names])
        before, after = bytecode(old), bytecode(new)
        if before != after:
            raise ValueError('undeclared executable/descriptor delta in presumed debug-only class; retain HOLD')
        result.append(dict(module=module, classes=keys, exactPrivateDescriptorsAndBytecodeEqual=True,
                           disassemblySha256=__import__('hashlib').sha256(after).hexdigest()))
    out = BASE/'PG5943-private-lock-debug20-v1'; os.umask(0o077); out.mkdir()
    public = dict(actualExit=0, source=value['source'], staticManifestSha256=sha(sp), physicalChanged=54, executableTargets=sorted(required),
                  debugOnlyClasses=sorted(others), moduleProofs=result, testsExecuted=0, productionMethodsInvoked=0, formalAccepted=False)
    with (out/'manifest.json').open('x') as f:
        json.dump(public, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=value['source'], executableTargets=34, otherClassBytecodeDescriptorsEqual=20, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
