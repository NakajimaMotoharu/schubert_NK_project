"""Publish original current3973 XML after qualification; never repeat tests or operations."""
import hashlib
import json
import os
from lan_server import run, copy
import pg5892_current3973_public as previous
from pg5928_api_storage_qualification import SOURCE, ROOT, W, SLOT as QUALIFIED, added_cases


def payload(data):
    raw = previous.payload(data).replace('PG5886', 'PG5926')
    if 'PG5886' in raw or 'Popen' in raw:
        raise ValueError('current original artifacts only')
    compile(raw, '<current3973 original XML allowlist>', 'exec')
    return raw


def terminal_trace(cases, prior):
    result = []
    for design in prior:
        hashes = {hashlib.sha256(s.encode()).hexdigest() for s in (design['method'], design['method']+'()')}
        found = [r for r in cases if r['class'] == design['class'] and r['caseNameSha256'] in hashes]
        if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML':
            raise ValueError('one actual current whole XML for each existing terminal contract')
        result.append(dict(klass=design['class'], **{'class': design['class']}, method=design['method'], designTestId=design['designTestId'], actualWholeTestId=found[0]['testId'], xmlSha256=found[0]['xmlSha256']))
    if len(result) != 6 or {r['designTestId'] for r in result} != {'PT-JMS-TERM'+str(i).zfill(3) for i in range(1, 7)}:
        raise ValueError('all existing six terminal contracts; no new Test cases')
    return result


def main():
    qp = W / QUALIFIED / 'manifest.safe.json'; receipt = json.loads(qp.read_bytes()); q = receipt['result']
    if not (receipt['actualExit'] == 0 and q['productionSource'] == SOURCE and (q['tests'], q['suites'], q['mainClasses']) == (3973, 592, 1666) and q['FESFlakyNotRun'] == q['staticSixModules'] == 0 and added_cases() == []):
        raise ValueError('independently qualified current3973 original first')
    data = dict(source=SOURCE, serverManifestSha256=q['serverManifestSha256'], archiveSha256=q['sourceArchiveSha256'], modules=q['modules'])
    raw = payload(data); digest = hashlib.sha256(raw.encode()).hexdigest()
    os.umask(0o077); out = W / 'pg5930-current3973-projection-v1'; out.mkdir(mode=0o700); path = out / 'project.private.py'
    with path.open('x') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    remote = '/home/mini/schubert-nk-pgpt/transfer/PG5930-case-reader-v1'
    code, _ = run('mkdir -m700 '+remote, timeout=30)
    if code:
        raise ValueError('new artifact reader namespace unavailable; no alternate route')
    code, _ = copy(path, remote+'/', timeout=60)
    if code:
        raise ValueError('fixed artifact reader transfer failed')
    code, text = run('sha256sum '+remote+'/project.private.py', timeout=30)
    if code or text.split()[0] != digest:
        raise ValueError('exact reader payload')
    code, text = run('python3 -B '+remote+'/project.private.py', timeout=180)
    with (out/'observer.private.log').open('x') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    if code:
        raise ValueError('original artifact reader failed; never replay PT for collection')
    cases = json.loads(next(s for s in reversed(text.splitlines()) if s.startswith('[')))
    if len(cases) != 3973 or len({r['testId'] for r in cases}) != 3973 or any(r['result'] != 'PASS_ORIGINAL_XML' or r['xmlSha256'] != q['modules'][r['module']]['xmlHashes'][r['sourceXml']] for r in cases):
        raise ValueError('all actual current3973 XML identities/results/hashes')
    base = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    oldp = base/'PG5886-current3973-cases/qualification.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest() != '2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f':
        raise ValueError('historical terminal design identities only, not current PASS')
    trace = terminal_trace(cases, json.loads(oldp.read_bytes())['currentTerminalContractTrace'])
    public = base/'PG5926-current3973-cases'; public.mkdir()
    cases_sha = hashlib.sha256((json.dumps(cases, ensure_ascii=False, indent=2)+'\n').encode()).hexdigest()
    value = {**q, 'currentTerminalContractTrace': trace, 'newCaseTestIdTrace': [], 'newTestCasesAdded': 0,
             'casesSha256': cases_sha, 'qualificationReceiptSha256': hashlib.sha256(qp.read_bytes()).hexdigest(),
             'projectionActualExit': code, 'projectionPayloadSha256': digest, 'historicalDesignManifestSha256': hashlib.sha256(oldp.read_bytes()).hexdigest(),
             'wholeReplayed': False, 'newSourceNativeQualified': False, 'acceptedLeafDelta': 0, 'effortPercent': None,
             'ptAlternativeCompleted': 0, 'globalSpecificationAcceptance': False}
    for name, body in (('cases.json', cases), ('qualification.json', value)):
        with (public/name).open('x') as f:
            json.dump(body, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, tests=3973, suites=592, mainClasses=1666, newTestCasesAdded=0,
                         terminalContractsTraced=6, allSeventeenTargetFour100=q['allSeventeenTargetFour100'],
                         summarySha256=hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(), casesSha256=cases_sha, formalAccepted=False)))


if __name__ == '__main__':
    main()
