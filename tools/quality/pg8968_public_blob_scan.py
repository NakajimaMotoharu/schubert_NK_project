"""G07 fixed tracked content scan, synthetic safety gate first; never print raw diagnostics."""
import base64
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from host_tool_invocation import capture, verify
from public_blob_scan import safe_path, sanitize, sha

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT.parent / 'pgpt-runs/PG379'
SLOT = WORK / 'pg8968-public-blob-scan-v1'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8968-public-blob-scan-v1'
CONTENT = '05d73a7974da8df92228160b96d91e7a006768f3'
SOURCE = 'fb9fce0f91de3d9fdfa634fe277592700f915e45'
BINARY = ROOT.parent / 'toolchain/gitleaks-8.30.1-linux-x64/gitleaks'
BINARY_SHA = '88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(SLOT)}


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    path.chmod(0o600)


def exclusive(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('xb') as stream:
        stream.write(data)
    path.chmod(0o600)


def scanner(root, phase, timeout):
    command = [str(BINARY), 'dir', str(root), '--config', str(SLOT / 'default.toml'),
               '--gitleaks-ignore-path', str(SLOT / 'empty.ignore'), '--ignore-gitleaks-allow',
               '--redact=100', '--report-format', 'json', '--report-path', '-',
               '--max-archive-depth', '0', '--max-decode-depth', '0',
               '--timeout', str(timeout), '--no-banner', '--no-color', '--log-level', 'error']
    begin = dt.datetime.now(dt.timezone.utc).isoformat()
    process = subprocess.Popen(command, cwd=SLOT, env=ENV, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    # This is our child only, not an inventory/read of any existing VM or target process.
    stat = Path('/proc') / str(process.pid) / 'stat'
    ticks = stat.read_text().rsplit(')', 1)[1].split()[19]
    write(SLOT / (phase + '-process.safe.json'), dict(pid=process.pid, pgid=process.pid,
          startTicks=ticks, beginUTC=begin, command=command, cwd=str(SLOT),
          binarySha256=BINARY_SHA, source=SOURCE, contentCommit=CONTENT))
    try:
        stdout, stderr = process.communicate(timeout=timeout + 60)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        raise TimeoutError('own scanner deadline') from None
    terminal = dict(actualExit=process.returncode, endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
                    stdoutBytes=len(stdout), stderrBytes=len(stderr), rawOutputPersisted=False)
    write(SLOT / (phase + '-terminal.safe.json'), terminal)
    if process.returncode not in (0, 1):
        raise ValueError('scanner failed; raw diagnostic suppressed')
    return stdout, terminal, command


def known_data(values):
    return {name: dict(sha256=sha(data), lines=data.count(b'\n') + 1) for name, data in values.items()}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists() and sha(BINARY.read_bytes()) == BINARY_SHA
    SLOT.mkdir(mode=0o700)
    stage = 'SYNTHETIC_OUTPUT_SAFETY'
    started = time.monotonic()
    try:
        exclusive(SLOT / 'default.toml', b'[extend]\nuseDefault = true\n')
        exclusive(SLOT / 'empty.ignore', b'')
        fixture = SLOT / 'synthetic'
        # Deterministic fictitious canaries, not usable credentials; never serialize their values.
        random_part = base64.b32encode(bytes.fromhex(sha(b'SCHUBERT-G07-FICTITIOUS-CANARY'))).decode()[:16]
        canary = ('AK' + 'IA' + random_part).encode()
        generic = sha(b'SCHUBERT-G07-SYNTHETIC-NON-CREDENTIAL').encode()
        values = {'positive.txt': b'aws_access_key_id = "' + canary + b'"\n',
                  'inline.txt': b'api_key = "' + generic + b'" # gitleaks:allow\n',
                  '.hidden/positive.txt': b'api_key = "' + generic + b'"\n',
                  'ignored/positive.txt': b'api_key = "' + generic + b'"\n',
                  '.gitignore': b'ignored/\n',
                  'safe.txt': b'Public non-credential documentation fixture.\n',
                  '.gitleaks.toml': b'[allowlist]\npaths = [\'\'\'.*\'\'\']\n'}
        for name, data in values.items():
            exclusive(fixture / name, data)
        raw, terminal, command = scanner(fixture, 'canary', 60)
        findings = sanitize(raw, known_data(values), fixture)
        detected = {row['path'] for row in findings}
        assert terminal['actualExit'] == 1 and {'positive.txt', 'inline.txt', '.hidden/positive.txt', 'ignored/positive.txt'} <= detected
        assert 'safe.txt' not in detected
        encoded = json.dumps(findings).encode()
        assert canary not in encoded and generic not in encoded
        write(SLOT / 'canary.safe.json', dict(actualExit=0, vendorExit=1, findings=findings,
             positiveDetected=True, inlineAllowIgnored=True, projectConfigIgnored=True,
             hiddenAndGitignoredFixturesDetected=True,
             safeFixtureUnflagged=True, rawOutputPersisted=False, command=command))
        # Never retain the unsanitized reporter bytes, including even redacted Match/context.
        del raw, canary, generic, values
        stage = 'FIXED_GIT_BLOB_MATERIALIZATION'
        assert subprocess.check_output(['git', 'rev-parse', CONTENT + '^{commit}'], cwd=ROOT).decode().strip() == CONTENT
        entries = subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', CONTENT], cwd=ROOT).split(b'\0')
        snapshot = SLOT / 'tracked'
        snapshot.mkdir(mode=0o700)
        rows = []
        unsupported = []
        git = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            for item in entries:
                if not item:
                    continue
                meta, encoded_name = item.split(b'\t', 1)
                mode, kind, oid = meta.decode('ascii').split()
                name = safe_path(encoded_name.decode('utf-8'))
                if kind != 'blob':
                    unsupported.append(dict(path=name, mode=mode, reason='NON_BLOB_GITLINK', gitObject=oid))
                    continue
                git.stdin.write((oid + '\n').encode()); git.stdin.flush()
                actual, actual_type, size = git.stdout.readline().decode('ascii').split()
                assert actual == oid and actual_type == 'blob'
                size = int(size)
                data = git.stdout.read(size)
                assert len(data) == size and git.stdout.read(1) == b'\n'
                assert hashlib.sha1(b'blob ' + str(size).encode() + b'\0' + data).hexdigest() == oid
                exclusive(snapshot / name, data)
                binary = b'\0' in data[:8192]
                archive = name.lower().endswith(('.zip', '.jar', '.gz', '.tgz', '.7z', '.xz', '.bz2', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.woff', '.woff2'))
                rows.append(dict(path=name, gitObject=oid, gitMode=mode, bytes=size, sha256=sha(data),
                    lines=data.count(b'\n') + 1, binaryPrefix=binary, containerOrImage=archive,
                    symbolicLinkTextOnly=mode == '120000',
                    inspectionLimit='BINARY_OR_CONTAINER_NO_INNER_SCAN' if binary or archive else None))
                del data
        finally:
            git.stdin.close(); git.wait(timeout=30)
        assert git.returncode == 0 and len({row['path'] for row in rows}) == len(rows)
        write(SLOT / 'inventory.safe.json', dict(contentCommit=CONTENT, rows=rows, unsupported=unsupported))
        stage = 'PUBLIC_FIXED_SNAPSHOT_SCAN'
        raw, terminal, command = scanner(snapshot, 'public', 1800)
        findings = sanitize(raw, {row['path']: row for row in rows}, snapshot)
        del raw
        assert (terminal['actualExit'] == 0) == (len(findings) == 0)
        verify(invocation)
        stage = 'SANITIZED_PUBLICATION'
        OUT.mkdir()
        write(OUT / 'inventory.json', dict(contentCommit=CONTENT, rows=rows, unsupported=unsupported))
        write(OUT / 'findings.json', findings)
        limits = [row['path'] for row in rows if row['inspectionLimit']]
        value = dict(actualExit=0, status='SCAN_COMPLETED_FINDINGS_REQUIRE_CLASSIFICATION' if findings else 'SCAN_COMPLETED_RULESET_LIMITED',
             timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), elapsedSeconds=round(time.monotonic() - started, 3),
             invocation=invocation, source=SOURCE, contentCommit=CONTENT, contentTree=subprocess.check_output(['git','rev-parse', CONTENT + '^{tree}'],cwd=ROOT).decode().strip(),
             scannerVersion='8.30.1', binarySha256=BINARY_SHA, os=platform.platform(), command=command,
             terminal=terminal, canarySha256=sha((SLOT / 'canary.safe.json').read_bytes()),
             inventorySha256=sha((OUT / 'inventory.json').read_bytes()), findingsSha256=sha((OUT / 'findings.json').read_bytes()),
             trackedBlobs=len(rows), bytes=sum(row['bytes'] for row in rows), findings=len(findings),
             findingRules=dict(Counter(row['ruleId'] for row in findings)), nonBlobUnsupported=unsupported,
             binaryOrContainerLimitedPaths=limits, binaryOrContainerLimitedCount=len(limits),
             defaultVendorAllowlistUnmodified=True, projectIgnoreOrBaselineUsed=False, inlineAllowIgnored=True,
             maximumArchiveDepth=0, maximumDecodeDepth=0, unsupportedNotPassed=True,
             actualVmActions=0, actualDbActions=0, actualTargetServiceConnections=0, privateCredentialReads=0,
             rawOutputPersisted=False, historicalCommitsScanned=False, untrackedOrPrivateInputsScanned=False,
             productTestsExecuted=0, productCoverage=None, formalUpdated=False, newAccepted=0,
             whole451SecretGateAccepted=False)
        write(OUT / 'manifest.json', value)
        print(json.dumps({key: value[key] for key in ('actualExit', 'status', 'trackedBlobs', 'bytes', 'findings', 'binaryOrContainerLimitedCount')}))
        return 0
    except Exception as error:
        failed = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8968-public-blob-scan-failed-v1'
        failed.mkdir()
        write(failed / 'manifest.json', dict(actualExit=1, stage=stage, errorType=type(error).__name__,
              invocation=invocation, source=SOURCE, contentCommit=CONTENT, rawDiagnosticSuppressed=True,
              partialOwnedSlotPreserved=True, productTestsExecuted=0, formalUpdated=False))
        print(json.dumps(dict(actualExit=1, stage=stage, errorType=type(error).__name__, rawDiagnosticSuppressed=True)))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
