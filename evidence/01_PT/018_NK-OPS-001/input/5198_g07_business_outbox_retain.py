"""Persist the exact retained scanner proof and release only the checked disposable projection."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ENTRY = Path(__file__).resolve()
spec = spec_from_file_location('g07_business_range', ENTRY.with_name('5196_g07_business_outbox_delta.py'))
r = module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    compact = r.load('g07_business_compact', '5184_g07_jdbc_metrics_retain_compact.py')
    r.configure(compact.w)
    compact.DETAILS = ('scan-terminal.json', 'qualified-cached-initial.json',
                       'qualified-final-private-detail.json', 'classified-findings.json',
                       'remaining-origins.json', 'binary-qualification.json',
                       'first-origin-tool-failure.json')
    p = compact.p
    raw = r.OUT / 'qualified-cached-initial.json'
    exact = p.load(raw)
    assert exact['confirmedSecrets'] == exact['unresolvedCandidates'] == exact['unqualifiedBinary'] == 0
    assert exact['resultQualifiedForRange'] and exact['trackedBlobVersions'] == 458
    p.write(r.OUT / 'qualified-final-private-detail.json', dict(exact, originProofTools=[
        p.ref(ENTRY.with_name(f)) for f in ('5196_g07_business_outbox_delta.py',
                   '5197_g07_business_outbox_origins.py', '5198_g07_business_outbox_retain.py')]))
    compact.main()


if __name__ == '__main__':
    main()
