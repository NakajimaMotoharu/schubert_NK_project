"""Bounded public Git-delta credential-format scan; never inspect runtime/private material."""
import argparse
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import ROOT, BASE, sha

BEFORE = 'd6ecb4cdb36459a56e273d76ccd97241176d6b09'
RULES = {
 'PRIVATE_KEY_PEM': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'GITHUB_CREDENTIAL': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),
 'AWS_ACCESS_KEY_ID': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')}


def inspect_bytes(raw):
    return [dict(rule=key, line=raw[:match.start()].count(b'\n') + 1) for key, rule in RULES.items() for match in rule.finditer(raw)]


def paths(raw):
    if not raw:
        return set()
    if not raw.endswith(b'\0'):
        raise ValueError('complete NUL-delimited Git paths')
    values = raw.decode('utf-8').split('\0')[:-1]
    if any(not value for value in values):
        raise ValueError('no empty path')
    return set(values)


def output(label):
    if not re.fullmatch(r'v[1-9][0-9]*', label):
        raise ValueError('new-only public scan revision, no arbitrary output path')
    return BASE / ('PG6908-public-delta-scan-' + label)


def main(label='v1'):
    out = output(label)
    names = paths(subprocess.check_output(['git', 'diff', '--name-only', '-z', BEFORE, '--'], cwd=ROOT))
    names.update(paths(subprocess.check_output(['git', 'ls-files', '-z', '--others', '--exclude-standard'], cwd=ROOT)))
    own = out.relative_to(ROOT).as_posix() + '/'
    names = {p for p in names if not p.startswith(own)}
    rows, findings = [], []
    for name in sorted(names):
        if not name.startswith(('src/', 'tools/quality/', 'documents/', 'evidence/01_PT/')) or '/private' in name or name.endswith('.private.log'):
            raise ValueError('scope is declared public project delta only')
        path = ROOT / name
        if path.is_symlink() or not path.is_file() or b'\0' in path.read_bytes():
            raise ValueError('only regular public text, unknown or binary is not a clean result')
        raw = path.read_bytes()
        rows.append(dict(path=name, sha256=sha(path), bytes=len(raw)))
        findings.extend(dict(path=name, **r) for r in inspect_bytes(raw))
    if not rows:
        raise ValueError('nonempty actual delta')
    value = dict(actualExit=1 if findings else 0, scope='DECLARED_PUBLIC_DELTA_PATTERN_SCAN_NOT_ALL_SECRETS_OR_RUNTIME',
      before=BEFORE, head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
      rules=list(RULES), files=rows, findings=findings, rawMatchValuesSaved=False,
      selfOutputExcludedOnly=own, testsExecuted=0, vmActions=0, formalAccepted=False, toolSha256=sha(ROOT / 'tools/quality/pg6908_public_delta_scan.py'))
    os.umask(0o077)
    out.mkdir()
    p = out / 'manifest.json'
    with p.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=value['actualExit'], files=len(rows), findings=len(findings), manifestSha256=sha(p))))
    return value['actualExit']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default='v1')
    raise SystemExit(main(parser.parse_args().label))
