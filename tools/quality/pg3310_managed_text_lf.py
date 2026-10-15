"""Read-only LF/UTF8 snapshot of managed documents/source/config, MSG009.

Not a secret scan or a claim over excluded binary/Current baseline evidence.
No file is normalized; violations are reported, never repaired here.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from pg3274_header_group_full_six import ROOT, SOURCE

SCOPES = ('documents', 'src', 'pom.xml', 'mvnw', '.mvn', 'README.md', 'AGENTS.md', '.gitattributes')
TEXT_SUFFIXES = {'.md', '.java', '.xml', '.sql', '.json', '.yaml', '.yml', '.sh', '.properties', '.service',
                 '.timer', '.conf', '.template', '.tsv', '.html', '.js', '.css', '.txt', '.py', '.cjs', '.jsonl'}


def selected(path):
    p = Path(path)
    return p.suffix in TEXT_SUFFIXES or p.name in ('mvnw', 'Caddyfile', '.gitattributes')


def inspect_text(data):
    try:
        data.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        return 'INVALID_UTF8'
    if b'\r' in data:
        return 'CR_NOT_LF_ONLY'
    if b'\x00' in data:
        return 'BINARY_NUL_NOT_MANAGED_TEXT'
    return 'PASS'


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('fixed clean text snapshot required')
    tracked = subprocess.check_output(['git', 'ls-files', '-z', *SCOPES], cwd=ROOT).decode().split('\0')
    files = []; excluded = []
    for name in filter(None, tracked):
        if not selected(name):
            excluded.append(name); continue
        data = (ROOT / name).read_bytes()
        files.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(),
                      'bytes': len(data), 'result': inspect_text(data)})
    failures = [f['path'] for f in files if f['result'] != 'PASS']
    value = {'actualExit': 1 if failures else 0, 'productionSource': SOURCE,
             'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'run': 'PG3310-managed-text-lf-v2', 'scope': list(SCOPES), 'files': files,
             'excludedUnknownOrBinarySuffixes': excluded, 'normalizedFiles': 0,
             'currentBaselineOrEvidenceOutsideScopeClaimed': False, 'secretScanClaimed': False,
             'formalUpdated': False, 'newPtCredit': 0, 'vmActions': 0}
    target = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG3310-managed-text-lf-v2'
    target.mkdir(parents=True, exist_ok=False)
    with (target / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False); stream.write('\n')
    print(json.dumps({'actualExit': value['actualExit'], 'textFiles': len(files),
                      'bytes': sum(f['bytes'] for f in files), 'excludedSuffixFiles': len(excluded), 'failures': failures}))
    return value['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
