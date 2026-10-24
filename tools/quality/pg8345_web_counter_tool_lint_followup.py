"""BUG1699 original successful metadata source preserved; lint-only correction, no PT replay."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

ORIGINAL_REF = '237d012598807afe8b3672e8d621caae0f14cd38'
TOOL = 'tools/quality/pg8344_web_counter_six_trace.py'
OUT = host.BASE / 'PG8345-web-counter-tool-lint-followup-v1'
TOOLS = ('pg8334_web_counter_six_compile.py', 'pg8336_web_counter_host.py',
         'pg8338_web_counter_fixed_six_compile.py', 'pg8340_web_counter_fixed_host.py',
         'pg8342_web_counter_post.py', 'pg8344_web_counter_six_trace.py',
         'pg8345_web_counter_tool_lint_followup.py')


def validate(before, after, expected):
    if hashlib.sha256(before).hexdigest() != expected or before.count(b'import hashlib\n') != 1 or before.replace(b'import hashlib\n', b'', 1) != after:
        raise ValueError('only exact unused-import correction allowed')


def main():
    invocation = capture(Path(__file__))
    witness = host.BASE / 'PG8344-web-counter-six-trace-v1/manifest.json'
    if OUT.exists() or host.sha(witness) != '653ca5c6a98a4938ae9d5aed852cf8dbf7eec63f9b9e8905bf7a1a3f20f54889':
        raise ValueError('new-only exact original receipt required')
    raw = json.loads(witness.read_text())
    if raw['actualExit'] != 0 or raw['source'] != '6c91f378543e9c1cbfa0c8a9dd3115f91cbbdccb':
        raise ValueError('exact original source/terminal required')
    before = subprocess.check_output(['git', 'show', ORIGINAL_REF + ':' + TOOL], cwd=host.ROOT)
    after = (host.ROOT / TOOL).read_bytes()
    expected = raw['invocation']['entrypointSha256']
    validate(before, after, expected)
    for path, digest in raw['invocation']['loadedProjectPythonSources'].items():
        if path != TOOL and host.sha(host.ROOT / path) != digest:
            raise ValueError('all other original tool inputs unchanged')
    rejected = 0
    for old, new in ((before + b'# changed\n', after), (before, after + b'# changed\n')):
        try:
            validate(old, new, expected)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('correction metadata negative must reject')
    command = ['python3', '-B', '-m', 'pyflakes', *['tools/quality/' + name for name in TOOLS]]
    environment = dict(PATH='/usr/bin:/bin', LANG='C.UTF-8', PYTHONPATH=str(host.TC / 'pyflakes-3.4.0/runtime'))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(command, cwd=host.ROOT, env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    if result.returncode != 0 or result.stdout or result.stderr or rejected != 2:
        raise ValueError('all seven public tools strict lint0 required before followup publication')
    verify(invocation)
    value = dict(actualExit=0, source=raw['source'], invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), bug='BUG-1699', rollout='YKT-1450', originalWitnessSha256=host.sha(witness), originalToolGitRef=ORIGINAL_REF + ':' + TOOL, originalToolSha256=expected, correctedToolSha256=host.sha(host.ROOT / TOOL), semanticChanges=False, originalQualityReplayed=False, lint=dict(command=command, environment=environment, startUTC=started, actualExit=result.returncode, stdoutSha256=hashlib.sha256(result.stdout).hexdigest(), stderrSha256=hashlib.sha256(result.stderr).hexdigest(), findings=0, inputHashes={name:host.sha(host.ROOT / ('tools/quality/' + name)) for name in TOOLS}), initialLintFinding='PG8344 unused hashlib import; original runtime proof exit0 is not a lint pass', metadataNegatives=rejected, productTestsExecuted=0, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, formalUpdated=False, newAccepted=0, effortPercent=None)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, lintTools=len(TOOLS), lintFindings=0, metadataNegatives=rejected, manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
