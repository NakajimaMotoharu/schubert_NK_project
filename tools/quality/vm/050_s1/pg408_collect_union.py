"""BUG412: reprocess preserved actual samples; do not start or re-observe the VM."""
import hashlib, json, pathlib, subprocess
repo = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
source = '32c6a7b1e79abf114901003c4a8f1300b33bf0c0'
assert json.loads((repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG408-root-recovery-baseline/manifest.json').read_text())['sourceCommit'] == source
assert (run/'pg408-native/root-api-observed.exec').stat().st_size == 0
roles = ['parent', 'backup', 'cleanup', 'expiry']
assert all((run/f'pg408-native/{role}.exec').stat().st_size > 0 for role in roles)
deps = pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
cp = [str(run), str(deps/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')]
cp.extend(str(deps/f'org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar') for name in ['asm','asm-tree','asm-commons'])
base = ['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java', '-cp', ':'.join(cp)]
coverage = {}
for module in ['protocol','storage','bootstrap','api','web','batch']:
    output = subprocess.check_output(base + ['NativeCoverage', str(repo/f'src/schubert-nk-{module}/target/classes'),
                    str(run/f'pg408-host/{module}.exec'), *[str(run/f'pg408-native/{role}.exec') for role in roles]])
    coverage[module] = json.loads(output)
    assert coverage[module]['classByteMismatch'] == 0
    (run/f'pg408-native/{module}-union.json').write_bytes(output)
missed = {kind: sum(v[kind]['missed'] for v in coverage.values()) for kind in ['BRANCH','LINE','METHOD','CLASS']}
print(json.dumps({'actualSampleRoles':roles,'rootEmptyExcluded':True,'ordinaryCoverageClaimed':False,
                  'classByteMismatch':0,'missed':missed,'vmMutation':False,'newExternalStart':False}))
