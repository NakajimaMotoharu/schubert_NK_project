"""Finite original scope declaration audit; saved exec metadata only, no Product replay."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE / 'PG17183-cycle-enum-finite-audit-v1'
PROOFS = [
    ('PG17138-root-scope-cleanup-value-seven-post-v1', 'da5ef53b38bb22d8f5dbea44be25dbae82755aea33bd6a507841309a0ae8e674', 0),
    ('PG17162-morning-launch-owner-three-post-v1', 'ff9ef6e9a9b77ad493e9dedd6e9557f40dac91bc8bc1987d8437ab34060185ab', 0),
    ('PG17182-morning-terminal-observation-seven-post-v1', '39cae7f6d2f1cc4376f468d97c1f26a8b6439bd786883afe368a14d1a4e94957', 5)]
ENUM = 'dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Outcome'


def assess(m, hits):
    assert m['actualExit'] == 0 and m['source'] == '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
    rows = m['syntheticBackupCycleProbeAudit']
    assert len(rows) == 23 and m['rootProbeAuditAllowedDataEnum'] == ENUM
    assert rows[ENUM] == dict(recordPresent=hits > 0, trueProbeHits=hits)
    assert all(v == dict(recordPresent=False, trueProbeHits=0) for n, v in rows.items() if n != ENUM)
    assert len(m['rootRecoveryProbeAudit']) == 5 and all(v == dict(recordPresent=False, trueProbeHits=0) for v in m['rootRecoveryProbeAudit'].values())
    assert len(m['reviewedInactiveBoundaryAudit']) == 10 and all(v == dict(recordPresent=False, trueProbeHits=0) for v in m['reviewedInactiveBoundaryAudit'].values())


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    observed = []
    failures = 0
    for folder, pin, hits in PROOFS:
        m = data.read_checked(data.BASE / folder / 'manifest.json', pin)
        assess(m, hits)
        verify(m['invocation'])
        observed.append(dict(manifest=folder, sha256=pin, enumHits=hits, operationalCycleRecords=0))
        changes = [lambda v: v['syntheticBackupCycleProbeAudit'][ENUM].update(trueProbeHits=hits + 1),
                   lambda v: v.update(rootProbeAuditAllowedDataEnum='wrong'),
                   lambda v: v['syntheticBackupCycleProbeAudit'].pop(ENUM),
                   lambda v: v['syntheticBackupCycleProbeAudit']['dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle'].update(recordPresent=True, trueProbeHits=1)]
        for change in changes:
            bad = copy.deepcopy(m); change(bad)
            try:
                assess(bad, hits)
            except (AssertionError, KeyError):
                failures += 1
            else:
                raise ValueError('scope distinction lost')
    old_path = data.ROOT / 'tools/quality/pg17184_morning_terminal_observation_seven_independent.py'
    new_path = data.ROOT / 'tools/quality/pg17185_morning_terminal_observation_seven_independent_v2.py'
    assert data.sha(old_path.read_bytes()) == 'f31734507a0f3a45f6324f652344ceee555e9d212428996a8e1a8351fbc030a9'
    assert data.sha(new_path.read_bytes()) == 'f38eda19efcbd23c81e94f77a1cab49c40dcf67639648969537277c4a44cb207'
    assert "'all cycle records absent'" in old_path.read_text() and "'all22 actual cycle body records absent'" in new_path.read_text()
    post = data.read_checked(data.BASE / 'PG17185-morning-terminal-observation-seven-independent-v2/manifest.json', 'a1070a5f6f924d1efbcb73159cd294204a6e7d2ff18c962d6429b349af85645d')
    assert post['semanticNegativeVectors'] == 70 and post['independentOracleVectors'] == 7
    verify(post['invocation']); verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation,
        source=post['source'], finiteScopeProfiles=observed, independentMetadataNegativeVectors=failures,
        failedOriginalScriptSha256=data.sha(old_path.read_bytes()), correctedScriptSha256=data.sha(new_path.read_bytes()),
        oldFailureRetained=True, originalTestsReexecuted=0, qualityConditionsChanged=False,
        newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
