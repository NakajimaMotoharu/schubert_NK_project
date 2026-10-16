"""Fresh current recovered-data proof for a new candidate; no old Root authority."""
import hashlib
import json
from pyflakes.api import check
import pg4360_pool_bound_partial_sources as frozen
from pg4260_stable_admission_image import execute
from pg4420_shared_manager_full import W

SLOT = 'pg4434-current-candidate-admission-read-v1'


def payload():
    recovery = json.loads((W / 'pg4384-half-handoff-recover-v1/manifest.safe.json').read_bytes())
    from pg4384_half_handoff_recover import completed
    completed(recovery['result'])
    candidate = json.loads((W / 'pg4432-candidate-build-v1.safe.json').read_bytes())
    if candidate['actualExit'] != 0 or candidate['manifestSha256'] != '93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de' or not candidate['candidateNotDeployed']:
        raise ValueError('actual distinct signed new-source candidate required')
    raw = frozen.files()['post.py']
    if hashlib.sha256(raw.encode()).hexdigest() != 'd64b8c588d337609a9b788f7540df50de2fb61dd69e9351ef2745d536bf7835b':
        raise ValueError('fixed original completed independent read profile required')
    marker = "save=base/'pg4362-pool-bound-post-v3'"
    if raw.count(marker) != 1: raise ValueError('one new-only private evidence namespace')
    raw = raw.replace(marker, "save=base/'" + SLOT + "'", 1)
    end = "(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))"
    if raw.count(end) != 1: raise ValueError('one final new proof boundary')
    addition = """
value.update(freshCandidateAdmissionDataOnly=True, priorRecoveryNotReplayed=True, oldParentNormal=False,
             candidateDeployed=False, candidateNativeCredit=False, fullSnapshotFields=len(post2),
             nativePhysicalFiles=sum(v.get('sha256') is not None for v in post2['native'].values()),
             startupPhysicalFiles=sum(v.get('sha256') is not None for v in post2['startup'].values()))
"""
    raw = raw.replace(end, addition + end, 1)
    if check(raw, '<fresh recovered-current candidate admission>'): raise ValueError('all emitted static0')
    return raw


def authenticate_host():
    from pg4152_exact_failed_done_recover import process
    from pg3428_vm_candidate_preflight_readonly import HOST
    from lan_server import run
    if process(20445) != {'pid': 20445, 'ticks': 104194, 'argvSha256': 'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:
        raise ValueError('fresh exact forward ownership required; no boot fallback')
    status, output = run(HOST, timeout=30)
    if status != 0 or json.loads(output)['boot'] != 'c7964823-c628-4ef2-99b5-07b0f0b62bba':
        raise ValueError('same current QEMU/chain/host required; no duplicate VM')


def main():
    authenticate_host()
    return execute(SLOT, payload(), 200)


if __name__ == '__main__':
    raise SystemExit(main())
