"""New-only isolated six-module literal proposal/full semantic proof; never applies Main."""
import hashlib
import inspect
import json
import os
import subprocess
from pathlib import Path
from lan_server import copy, run
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require

NAMES = ['IsolatedSourceOutput.java', 'SourcePrivateFieldRename.java', 'SourceStringLiteralConstants.java', 'SourceStringLiteralProof.java']


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import shutil
    import subprocess
    os.umask(0o077); b = Path('/home/mini/schubert-nk-pgpt'); out = b / 'runs/PG3952-literal-candidate-v1'; transfer = b / 'transfer/PG3952-literal-candidate-v1'
    require(shutil.disk_usage(b).free > 12 * 1024**3, 'new isolated work plus preservation capacity')
    out.mkdir(); (out / 'classes').mkdir(); source = b / 'source-full-PG3928'; candidate = out / 'candidate'; sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    require({str(p.relative_to(source)): sha(p) for p in source.glob('src/*/src/main/java/**/*.java')} == data['sourceSha256'], 'all849 original source exact')
    whole = b / 'runs/PG3930-current-boundary-whole-qualified-v1/manifest.safe.json'; require(sha(whole) == data['wholeQualificationSha256'], 'genuine3716 source authority')
    report = b / 'runs/PG3864-suppression-identity-review-v1/all1840-dispositions.safe.json'; require(sha(report) == data['originalFindingSha256'], 'original source-bound coordinates/187 target findings')
    findings = [r for r in json.loads(report.read_bytes()) if r['rule'] == 'AvoidDuplicateLiterals']; require(len(findings) == 187, 'all187 original findings')
    require(all(r['sourceSha256'] == data['sourceSha256'][r['path']] for r in findings), 'each finding exact source byte')
    cpfile = b / 'runs/PG3690-import-candidate-v1/manifest.safe.json'; require(sha(cpfile) == data['classpathAuthoritySha256'], 'immutable typed dependency graph')
    prior = json.loads(cpfile.read_bytes()); tools = data['toolSha256']
    require(all(sha(transfer / n) == h for n, h in tools.items()), 'fixed complete tool/formatter closure')
    java = b / 'tools/jdk-25.0.4/bin/java'; javac = java.parent / 'javac'
    compiled = subprocess.run([str(javac), '-Xlint:all', '-Werror', '-d', str(out / 'classes'), *[str(transfer / n) for n in tools if n.endswith('.java')]], capture_output=True, timeout=30)
    (out / 'compile.private.log').write_bytes(compiled.stdout + compiled.stderr); require(compiled.returncode == 0 and not compiled.stderr, 'all compiler tools lint0')
    start = datetime.datetime.now(datetime.timezone.utc).isoformat(); (out / 'begin.safe.json').write_text(json.dumps({'source': data['source'], 'operatorHead': data['head'], 'startUTC': start, 'pid': os.getpid(), 'ticks': int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]), 'MainApplied': False, 'vmActions': 0}))
    shutil.copytree(source, candidate, ignore=shutil.ignore_patterns('target', '.git'))
    def cp_hash(cp):
        values = {}
        for p in map(Path, cp.split(':')):
            require(p.is_absolute() and p.exists(), 'exact absolute type dependency')
            values[str(p)] = {str(x.relative_to(p)): sha(x) for x in p.rglob('*') if x.is_file() and x.suffix in {'.java', '.class'}} if p.is_dir() else sha(p)
        return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()
    plans = {}; proposals = []; held = []
    for module, item in prior['modules'].items():
        relative = 'src/schubert-nk-' + module + '/src/main/java'; prefix = relative + '/'; cp = item['phases']['after']['command'][-1]
        require(cp_hash(cp) == item['classpathInputsSha256'], 'all real frozen type inputs')
        selected = [r for r in findings if r['path'].startswith(prefix)]; requests = out / (module + '-requests.tsv')
        requests.write_text(''.join(r['path'][len(prefix):] + '\t' + str(r['coordinates']['beginline']) + '\t' + str(r['coordinates']['begincolumn']) + '\n' for r in selected))
        generated = out / ('generated-' + module)
        args = [str(java), '-Xmx1536m', '-cp', str(out / 'classes'), 'SourceStringLiteralConstants', str(source / relative), cp, str(requests), str(generated)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=180); (out / (module + '-plan.safe.tsv')).write_text(result.stdout); (out / (module + '-plan.private.log')).write_text(result.stderr)
        require(result.returncode == 0, 'actual bounded source proposal ' + module)
        for line in result.stdout.splitlines():
            if line.startswith('CONSTANT\t'): proposals.append({'module': module, 'fields': line.split('\t')})
            elif line.startswith('HELD\t'): held.append({'module': module, 'fields': line.split('\t')})
        for p in generated.rglob('*.java'): shutil.copyfile(p, candidate / relative / p.relative_to(generated))
        plans[module] = {'requests': len(selected), 'planSha256': sha(out / (module + '-plan.safe.tsv')), 'actualExit': 0}
        require(cp_hash(cp) == item['classpathInputsSha256'], 'all type inputs remain unchanged')
        (out / 'progress.safe.json').write_text(json.dumps({'proposalModules': list(plans), 'constants': len(proposals), 'held': len(held), 'MainApplied': False}))
    files = sorted(candidate.glob('src/*/src/main/java/**/*.java')); require(len(files) == 849, 'all849 candidate regular source copies')
    formatted = subprocess.run([str(java), '-Xmx1536m', '-jar', str(transfer / 'google-java-format-1.36.1-all-deps.jar'), '--skip-reflowing-long-strings', '--replace', *map(str, files)], capture_output=True, timeout=120)
    (out / 'format.private.log').write_bytes(formatted.stdout + formatted.stderr); require(formatted.returncode == 0, 'fixed formatter0')
    modules = {}
    for module, item in prior['modules'].items():
        relative = 'src/schubert-nk-' + module + '/src/main/java'; cp = item['phases']['after']['command'][-1]; require(cp_hash(cp) == item['classpathInputsSha256'], 'same proof type dependencies')
        args = [str(java), '-Xmx1536m', '-cp', str(out / 'classes'), 'SourceStringLiteralProof', str(source / relative), str(candidate / relative), cp, str(out / (module + '-plan.safe.tsv'))]
        result = subprocess.run(args, capture_output=True, text=True, timeout=180); (out / (module + '-proof.safe.tsv')).write_text(result.stdout); (out / (module + '-proof.private.log')).write_text(result.stderr)
        require(result.returncode == 0 and result.stdout.startswith('FULL_SEMANTIC_ABI_VALUES_IDENTICAL\t'), 'all original values/type/member bindings/full AST/public ABI proof ' + module)
        require(cp_hash(cp) == item['classpathInputsSha256'], 'type proof inputs unchanged afterward')
        modules[module] = {'actualExit': 0, 'sourceFiles': item['sourceFiles'], 'proofSha256': sha(out / (module + '-proof.safe.tsv'))}
        (out / 'progress.safe.json').write_text(json.dumps({'semanticModules': list(modules), 'MainApplied': False}))
    changes = {str(p.relative_to(candidate)): {'before': data['sourceSha256'][str(p.relative_to(candidate))], 'candidate': sha(p)} for p in files if sha(p) != data['sourceSha256'][str(p.relative_to(candidate))]}
    require(changes and not set(changes) & set(data['generatedFiles']), 'generated70 artifacts unchanged')
    require({str(p.relative_to(source)): sha(p) for p in source.glob('src/*/src/main/java/**/*.java')} == data['sourceSha256'], 'all original source bytes unchanged')
    value = {'actualExit': 0, 'baseProductionSource': data['source'], 'operatorHead': data['head'], 'sourceFiles': 849, 'requestedFindings': 187,
             'proposedConstants': len(proposals), 'held': held, 'proposals': proposals, 'changes': changes, 'changedFiles': len(changes), 'modules': modules,
             'allValuesTypedBindingsFullAstAndPublicAbiIdentical': True, 'privateCompileTimeStringFieldsOnly': True, 'generated70Unchanged': True,
             'allCandidateSourceSha256': {str(p.relative_to(candidate)): sha(p) for p in files}, 'formatExit': 0, 'fixedStaticPending': True, 'MainApplied': False,
             'F03Accepted': False, 'formalAccepted': False, 'vmActions': 0, 'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); value['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed candidate operator')
    full = json.loads((W / 'pg3930-current-boundary-whole-qualified-v1/manifest.safe.json').read_bytes()); require(full['actualExit'] == 0 and full['result']['tests'] == 3716, 'completed current3716 first')
    require(not subprocess.check_output(['git', 'diff', full['result']['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT), 'actual qualified Main/Test/settings unchanged')
    original = json.loads((W / 'pg3864-suppression-identity-review-v1/manifest.safe.json').read_bytes())['result']; typed = json.loads((W / 'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes())['result']
    generated = json.loads((ROOT / 'evidence/01_PT/006_NK-MSG-002/evidence/quality/generation-results.json').read_bytes())['generatedSha256']
    require(len(generated) == 70, 'all70 reproducible artifacts')
    tools = [*[ROOT / 'tools/quality' / n for n in NAMES], Path('/home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar')]
    data = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'wholeQualificationSha256': full['result']['qualificationManifestSha256'], 'originalFindingSha256': original['dispositionsSha256'],
            'classpathAuthoritySha256': typed['serverManifestSha256'], 'sourceSha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')},
            'generatedFiles': ['src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/' + n for n in generated],
            'toolSha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tools}}
    require(data['toolSha256']['google-java-format-1.36.1-all-deps.jar'] == '25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4', 'exact project formatter')
    os.umask(0o077); out = W / 'pg3952-literal-candidate-v1'; out.mkdir()
    script = out / 'candidate.private.py'; script.write_text('INPUT=' + repr(data) + '\n' + inspect.getsource(require) + '\n' + inspect.getsource(server) + '\nserver(INPUT)\n')
    compile(script.read_text(), '<isolated current literal candidate>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG3952-literal-candidate-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3952-literal-candidate-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only isolated candidate')
    for p in [*tools, script]:
        status, _ = copy(p, destination + '/', timeout=60); require(status == 0, 'fixed complete candidate inputs')
    status, output = run('python3 -B ' + destination + '/candidate.private.py', timeout=1500); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'MainApplied': False, 'F03Accepted': False}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if status == 0: print(json.dumps({k: value['result'][k] for k in ['requestedFindings', 'proposedConstants', 'held', 'changedFiles', 'serverManifestSha256']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
