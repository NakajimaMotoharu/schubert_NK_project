"""Scan the frozen public patch and verify scanner candidates by independent provenance."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


PMO = Path('documents/400_PGPT/470_PMO')
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
SCAN = Path('../toolchain/gitleaks-8.30.1-linux-x64/gitleaks')
SUFFIXES = {'.md','.java','.py','.json','.xml','.tsv','.txt','.patch'}
DOMAIN = ('src/','evidence/01_PT/','documents/400_PGPT/','documents/900_OTHER/910_台帳/','tools/quality/')
BASELINE = 'program/characterization/baseline/current'
GIT_ID_FIELD = re.compile(rb'^[ +-]?\s*"([A-Za-z][A-Za-z0-9_]*)": "([0-9a-f]{40})"\s*,?\s*$')
OID_KEYS = {'source','sourceCore','productionCore','productionCoreMain','canonicalDesignSource',
            'headBeforeCheckpoint','remoteBeforeCheckpoint','canonicalDesign','releasedSource',
            'headInclusive','baseExclusive','toolSource','sourceBeforeEvidence','commit',
            'sourceHeadBeforeRecord','remoteHeadBeforeRecord','receivedSource'}


def fetch_git(*args):
    return subprocess.check_output(['git',*args],timeout=25)


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def main():
    start, = PMO.glob('601_*/1613_*.json')
    v = json.loads(start.read_bytes())['values']
    assert all(pin(Path(ref['path']))==ref for ref in v['oracleReferences'])
    prior = Path(v['oracleReferences'][1]['path'])
    base = json.loads(prior.read_bytes())['headInclusive']
    head = v['source']
    assert fetch_git('rev-parse','HEAD','origin/dev-foundation').decode().splitlines()==[head,head]
    assert fetch_git('merge-base',base,head).decode().strip()==base
    baseline = fetch_git('rev-parse',f'{head}:{BASELINE}').decode().strip()
    assert fetch_git('rev-parse',f'{base}:{BASELINE}').decode().strip()==baseline
    commits = fetch_git('rev-list','--reverse',f'{base}..{head}').decode().splitlines()
    assert commits
    files, patches, lines = {}, [], []
    for commit in commits:
        parents = [commit+'^',commit]
        names = fetch_git('diff','--name-only','-z',*parents).decode().split('\0')[:-1]
        assert all(n.startswith(DOMAIN) and Path(n).suffix in SUFFIXES
                   and not n.endswith(('.safe.json','.raw.txt')) for n in names)
        patch = fetch_git('diff','--no-renames','--no-ext-diff','--unified=0',*parents)
        assert not any(line.startswith((b'Binary files ',b'GIT binary patch')) for line in patch.splitlines())
        patches.append(patch)
        lines.append(dict(commit=commit,changedPaths=len(names),patchSha256=sha256(patch).hexdigest()))
        for name in names:
            data = fetch_git('diff','--no-renames','--no-ext-diff','--unified=0',*parents,'--',name)
            files.setdefault(name,[]).append(data)
    whole = b'\n'.join(patches)
    reports = []
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-public-scan-') as temp:
        report = Path(temp)/'combined.json'
        flags = [str(SCAN),'stdin','--redact=100','--no-banner']
        full = subprocess.run([*flags,'--report-format','json','--report-path',str(report)],
                              input=whole,capture_output=True,timeout=45)
        assert full.returncode in (0,1) and report.is_file()
        candidates = json.loads(report.read_bytes()) or []
        raw_lines = whole.splitlines()
        unclassified = []
        for finding in candidates:
            index = finding['StartLine']
            match = GIT_ID_FIELD.match(raw_lines[index-1]) if 1<=index<=len(raw_lines) else None
            rule = finding['RuleID']
            is_commit = bool(rule=='sourcegraph-access-token' and match and match[1].decode() in OID_KEYS
                             and subprocess.run(['git','cat-file','-t',match[2].decode()],
                                 capture_output=True,timeout=5).stdout==b'commit\n')
            reports.append(dict(rule=rule,line=index,admittedCommitId=is_commit,
                                field=match[1].decode() if is_commit else None))
            if not is_commit:
                unclassified.append(dict(rule=rule,line=index))
        per_path_failures = []
        for name, content in files.items():
            result = subprocess.run(flags,input=b'\n'.join(content),capture_output=True,timeout=25)
            if result.returncode:
                per_path_failures.append(dict(path=name,exit=result.returncode))
    ok = not unclassified and not per_path_failures
    out = OPS/v['run']
    out.mkdir()
    target = out/'manifest.json'
    summary = dict(actualExit=int(not ok),terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                   core=v['productionCoreMain'],baseExclusive=base,headInclusive=head,baselineTree=baseline,
                   previousScan=pin(prior),perCommit=lines,commits=len(commits),uniquePaths=len(files),
                   patchStreamSha256=sha256(whole).hexdigest(),combinedScanExit=full.returncode,
                   rawCandidates=len(reports),candidateClassification=reports,unclassified=unclassified,
                   perPathFailures=per_path_failures,detected=0 if ok else None,
                   detectorRulesChanged=False,secretValuesPrinted=0,privateObjectsRead=0,
                   nativeOrProductOperations=0,whole451=False,formalDelta=0)
    with target.open('x') as f:
        json.dump(summary,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(target),len(commits),len(files),len(reports),len(unclassified),len(per_path_failures))
    return int(not ok)


if __name__=='__main__':
    raise SystemExit(main())
