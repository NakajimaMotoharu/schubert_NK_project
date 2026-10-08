"""Publish only whitelisted PG672 technical data; never raw session IDs or logs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
T = R.parents[3]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg672-entry-six-host-v2')
OUT = T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG672-full-public-v1'


def main():
    os.umask(0o077)
    raw = (W/'manifest.safe.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'b66da36efa077a7f41bcfb9777fad702c986dccc07b872962db00495f378a26c'
    value = json.loads(raw)
    assert value['actualExit'] == value['staticIssues'] == value['FESFlakyNotRunIndicators'] == 0
    assert (value['tests'], value['suites'], value['mainClasses']) == (3477, 514, 1608)
    keys = ('actualExit', 'run', 'candidateSource', 'collectorOperator',
            'installedVmSource', 'candidateNotDeployed', 'sourceQualification',
            'tests', 'suites', 'mainClasses', 'allMainBytesEqualSelectedCandidate',
            'FESFlakyNotRunIndicators', 'staticModules', 'staticIssues')
    public = {k: value[k] for k in keys}
    public['modules'] = {k: {field: item[field] for field in
                            ('tests', 'suites', 'FESFlakyNotRun', 'staticIssues', 'hostCounters')}
                         for k, item in value['moduleResults'].items()}
    public.update(privateQualificationSha256=hashlib.sha256(raw).hexdigest(),
                  publisherOperator=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
                  formalAccepted=False, coverage100=False,
                  rawLogsAndSessionIdsExcluded=True,
                  testSpecification='549_PG672v2_正規六member回帰再試験.md')
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(public, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'actualExit': 0, 'publicSha256': hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),
                      'privateDataPublished': False, 'formalAccepted': False}))


if __name__ == '__main__':
    main()
