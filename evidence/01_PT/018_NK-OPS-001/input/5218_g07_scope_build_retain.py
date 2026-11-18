"""Preserve the fixed scan range and release only the hash-checked temporary projection."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ENTRY=Path(__file__).resolve()
spec=spec_from_file_location('g07_scope_archive',ENTRY.with_name('5216_g07_scope_build_delta.py'))
r=module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    compact=r.load('g07_scope_compact_retain','5184_g07_jdbc_metrics_retain_compact.py')
    r.configure(compact.w)
    compact.DETAILS=('scan-terminal.json','qualified-cached-initial.json',
                     'qualified-final-private-detail.json','classified-findings.json',
                     'remaining-origins.json','binary-qualification.json')
    p=compact.p
    exact=p.load(r.OUT/'qualified-cached-initial.json')
    assert exact['confirmedSecrets']==exact['unresolvedCandidates']==exact['unqualifiedBinary']==0
    assert exact['resultQualifiedForRange'] and exact['trackedBlobVersions']==172
    assert exact['commits']==8 and sum(exact['categories'].values())==exact['findingsCount']==82
    p.write(r.OUT/'qualified-final-private-detail.json',dict(exact,proof=[p.ref(ENTRY.with_name(file))
        for file in ('5216_g07_scope_build_delta.py','5217_g07_scope_build_origins.py',
                     '5218_g07_scope_build_retain.py')]))
    compact.main()


if __name__=='__main__':
    main()
