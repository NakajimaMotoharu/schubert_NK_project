"""SS355 tool-only input oracle. Never opens actual baseline/reports/captures."""
from pathlib import Path
import json, hashlib, shutil

DESIGN = ('cases/gate-contract.json','cases/catalog.json','cases/schema.json',
          'cases/dif-allowlist.json','browser/manifest.json','cases/case-requirements.json')

def build(repo, root):
    repo, root = Path(repo), Path(root)
    assert not root.exists() and root.resolve() != repo.resolve()
    resources = root/'program/characterization/tests/resources'
    resources.mkdir(parents=True)
    pins = {}
    for name in DESIGN:
        src = repo/'program/characterization/tests/resources'/name
        target = resources/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        pins[str(src.relative_to(repo))] = hashlib.sha256(src.read_bytes()).hexdigest()
    load = lambda p: json.loads(p.read_text())
    def write(p, value):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    contract = load(resources/'cases/gate-contract.json')
    required = load(resources/'cases/case-requirements.json')
    # Fixed fake values, not any real source/master inventory. They are metadata test inputs.
    source = {k: (('1' if 'source' in k else '2')*64 if k.endswith('Sha256') else 1)
              for k in contract['source']}
    contract['source'] = source
    reports = root/'program/characterization/reports'
    write(reports/'source-verification.json', dict(source,status='PASS',masterSymlinks=[]))
    write(reports/'preflight.json',dict(status='PASS',failures=[],credentialPermission='0600',
        hostAllowlist=['localhost','127.0.0.1'],freeBytes=21474836480))
    write(reports/'review-record.json',dict(status='APPROVED',baselineCommit='843de94',
        reviewerRole='SYNTHETIC_TEST_DATA_NOT_ACTUAL_APPROVAL',evidence=['fake-a','fake-b','fake-c'],
        checks={k:True for k in ['currentSourceUnchanged','currentMasterUnchanged','repeatDiffZero',
                               'secretScanZero','qaThrough044Resolved','uicThrough004Completed']}))
    write(reports/'current-repeat-comparison.json',dict(status='PASS',firstFileCount=28,
        secondFileCount=28,missing=[],extra=[],changed=[]))
    # Deliberately non-image bytes: validator hashes opaque files, no actual screenshot/browser claim.
    screenshot = b'SYNTHETIC-OPAQUE-SCREENSHOT-ONLY\n'
    screenshot_hash = hashlib.sha256(screenshot).hexdigest()
    baseline = root/'program/characterization/baseline/current'
    for run in [baseline, reports/'current/pgpt-gate-20260901-05',
                reports/'current/pgpt-gate-20260901-06']:
        for case, keys in required['requirements'].items():
            item = {k:'synthetic-not-an-observation' for k in keys}
            item.update(caseId=case,status='PASS')
            if case == 'CHR-U01':
                item.update(desktopScreenshotSha256=screenshot_hash,mobileScreenshotSha256=screenshot_hash)
            write(run/'artifacts'/(case+'.json'),item)
        for name in ['CHR-U01-desktop.png','CHR-U01-mobile.png']:
            p=run/'screenshots'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(screenshot)
        if run != baseline:
            write(run/'inventory.json',dict(source,status='PASS'))
            write(run/'supplemental.json',dict(checks={case:{check:dict(status='PASS',evidence=dict(synthetic=True))
                for check in checks} for case,checks in required['supplementalChecks'].items()}))
    write(baseline/'manifest.json',dict(target='current',caseCount=24,screenshotFileCount=2,
        differenceCount=16,gateCommit='commit-containing-this-manifest',
        **{k:source[k] for k in ['sourceAggregateSha256','documentAggregateSha256','masterFileCount','masterBytes']},
        environment=dict(javaVersion='25.0.4',browserRevision=1187,locale='ja-JP',timezone='Asia/Tokyo')))
    files = sorted((p for p in baseline.rglob('*') if p.is_file()),
                   key=lambda p:p.relative_to(root).as_posix().encode('utf-8'))
    assert len(files)==27
    lines = ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n'
                    for p in files)
    contract['baselineAggregateSha256']=hashlib.sha256(lines.encode('utf-8')).hexdigest()
    write(resources/'cases/gate-contract.json',contract)
    all_pins={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in root.rglob('*') if p.is_file()}
    return dict(publicDesignInputHashes=pins,syntheticInputHashes=all_pins,
                baselineAggregateLines=lines,baselineAggregateSha256=contract['baselineAggregateSha256'],
                actualBaselineAccess=False,actualApproval=False,actualScreenshot=False)
