"""Verify and preserve a separate decision for each raw PMD finding in the three-file run."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
from xml.etree import ElementTree as ET

O = Path('evidence/01_PT/018_NK-OPS-001/evidence/PG39984-f03-batch-three-current-pmd-v1')
SS = {
    'SS332': 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md',
    'SS341': 'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md',
    'SS342': 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
}
CANON = '5aafdc4bff5e8a4c15db9a8000ddf3f1fd17f774'
CATCH = 'AvoidCatchingGenericException'
TYPE = 'AvoidInstanceofChecksInCatchClause'
THREAD = 'DoNotUseThreads'
REVIEW = {
    'BackupCommitService.java': [
        ((35,), CATCH, 'Before transaction commit, one rollback and auto-commit recovery is attempted for each typed failure; successful recovery rethrows the original.'),
        ((39,), CATCH, 'The rollback/setAutoCommit failure is secondary; preserve unknown original/cleanup identity and choose the fixed repository error only after fatal graph checks.'),
        ((40,41,42), TYPE, 'These type checks select the separately captured original unknown Error/runtime identity and a fixed secondary diagnostic.'),
        ((46,47,48), TYPE, 'Only when original is known, choose the separately captured unknown rollback/restore Error or RuntimeException; otherwise inspect both fatal graphs.'),
        ((65,), THREAD, 'Only reads current thread interrupt status before admitted work; no Thread is created or scheduled.'),
    ],
    'LogCleanupService.java': [
        ((89,93), THREAD, 'Only reads current thread interrupt status before and after the clock observation; no Thread is created or scheduled.'),
        ((125,), CATCH, 'Owned advisory lock release is called after callback failures of each eligible category; an original is rethrown unless approved cleanup precedence selects secondary.'),
        ((128,), CATCH, 'An actual release failure is a separate throwable from the failed action; replace applies known/unknown precedence and safe suppression.'),
        ((187,), CATCH, 'Durable committed chunks bypass rollback; before commit a failing mutation uses rollback and restore, preserving the original if recovery succeeds.'),
        ((192,), CATCH, 'Rollback/restore failure priority is separately applied via known, fixed secondary diagnostics, and finite fatal graph checks.'),
        ((231,279), CATCH, 'Each held JDBC row saves and rethrows the actual primary for its single close helper during both advisory acquisition and release.'),
        ((237,285), CATCH, 'Each held JDBC statement saves and rethrows its actual primary for single close after nested row closure during acquisition and release.'),
        ((249,), CATCH, 'The row close helper alone applies primary/secondary precedence; qualifying secondary is rethrown, all later statement ownership remains outside this catch.'),
        ((258,), CATCH, 'The statement close helper alone applies primary/secondary precedence; the row is already finished before this helper.'),
    ],
    'StepCleanupService.java': [
        ((103,), CATCH, 'Durable committed chunks bypass rollback; otherwise rollback/restore handles each typed failure and rethrows original on successful recovery.'),
        ((108,), CATCH, 'Separately captured rollback/restore failure is compared against the original, including approved cleanup stop as a known category.'),
        ((110,111,112,113), TYPE, 'Priority of the separately captured original requires checking both fatal/runtime and two explicit known cleanup/repository types.'),
        ((117,118,119,120), TYPE, 'If original is known, a separately captured unknown/fatal cleanup failure wins. Both known failures receive independent fatal graph checks before fixed diagnostic.'),
        ((133,137), THREAD, 'Only reads current thread interrupt status before and after clock observation; no Thread is created or scheduled.'),
    ],
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return dict(path=str(path),sha256=sha(Path(path).read_bytes()))


def main():
    read = lambda path: json.loads(path.read_bytes())
    begin = read(O/'begin.json')
    terminal = read(O/'pmd-exit.json')
    main = read(O/'manifest.json')
    assert main['actualExit'] == 0 and main['realPmdExit'] == terminal['actualExit'] == 4
    assert main['raw']['processingErrors'] == 0
    assert begin['command'] == terminal['command']
    assert pin(begin['fullRules']['path']) == begin['fullRules']
    assert pin(main['raw']['raw']['path']) == main['raw']['raw']
    current = {p: subprocess.check_output(['git','show',f'{main["source"]}:{p}'],timeout=15)
               for p in begin['sourceInput']}
    assert {p:sha(raw) for p,raw in current.items()} == begin['sourceInput']
    assert {Path(p).name for p in current} == set(REVIEW)
    matrix = {}
    for file, groups in REVIEW.items():
        for lines, rule, reason in groups:
            for line in lines:
                coordinate = file,line,rule
                assert coordinate not in matrix
                matrix[coordinate] = reason
    assert len(matrix) == 33
    xml = ET.parse(O/'pmd.xml')
    nodes = [(f, v) for f in xml.findall('{*}file') for v in f.findall('{*}violation')]
    assert len(nodes) == len(main['rawFindings']) == 61
    assert not xml.findall('{*}error') and not xml.findall('{*}configerror')
    refs = {key:dict(path=path, sha256=sha(subprocess.check_output(['git','show',f'{CANON}:{path}'],timeout=15)))
            for key,path in SS.items()}
    counts, records = Counter(), []
    for i, (entry, (file, raw)) in enumerate(zip(main['rawFindings'],nodes,strict=True),1):
        assert Path(file.get('name')).is_absolute() and file.get('name').endswith('/'+entry['file'])
        assert int(raw.get('beginline')) == entry['start'] and int(raw.get('endline')) == entry['end']
        assert int(raw.get('begincolumn')) == entry['column'] and raw.get('rule') == entry['rule']
        assert (raw.text or '').strip() == entry['text']
        line = current[entry['file']].decode().splitlines()[entry['start']-1]
        coordinate = Path(entry['file']).name,entry['start'],entry['rule']
        counts[coordinate] += 1
        if entry['rule'] == THREAD:
            assert 'Thread.currentThread().isInterrupted()' in line
            decision, requirements = 'RULE_DOES_NOT_APPLY_TO_THREAD_STATUS_READ', ['SS341','SS342']
        elif entry['rule'] == CATCH:
            assert 'catch (SQLException | RuntimeException | Error' in line
            decision, requirements = 'TYPED_FAILURE_AND_OWNED_RESOURCE_CONTRACT', ['SS332','SS341']
        else:
            assert 'instanceof ' in line
            decision, requirements = 'TWO_FAILURE_IDENTITIES_AND_SPECIFIED_PRIORITY', ['SS332','SS341']
        records.append(dict(rawIndex=i, finding=entry, inputSha256=begin['sourceInput'][entry['file']],
                            lineSha256=sha(line.encode()), decision=decision,
                            scopeReason=matrix[coordinate], requirements=requirements))
    assert set(counts) == set(matrix)
    assert all(count == (1 if profile == THREAD else 2) for (_,_,profile),count in counts.items())
    result = dict(actualExit=0, source=main['source'], raw=pin(O/'pmd.xml'), manifest=pin(O/'manifest.json'),
                  productionRuleAndThresholdUnmodified=True, rawFindingCount=61, reviewedSiteCount=33,
                  applicable=0, unclassified=0, toolExit=4, processingErrors=0,
                  designsSource=CANON, designPins=refs, rows=records, noSuppressionAdded=True,
                  additionalProductTrials=0, wholeF03Accepted=False, whole451Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (O/'independent.json').open('x') as out:
        json.dump(result,out,indent=2,ensure_ascii=False)
        out.write('\n')
    print('61 raw findings reviewed at 33 sites; applicable 0; unclassified 0')


if __name__ == '__main__':
    main()
