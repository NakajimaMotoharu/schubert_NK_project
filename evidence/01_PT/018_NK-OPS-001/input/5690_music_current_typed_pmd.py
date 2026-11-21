"""Measure typed PMD on the current independently admitted 30 Web Main files."""

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

parent = Path(__file__).with_name('5686_scr011_012_template_current_six.py')
spec = importlib.util.spec_from_file_location('music_pmd_helpers', parent)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
RUN = 'PG41508-f03-music-current-typed-pmd-v1'


def local(tag):
    return tag.rsplit('}', 1)[-1]


def main():
    begin = h.read(next(h.PLAN.glob('1908_*')))
    q = begin['quota']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(q['observedAtUTC'])
    assert q['ordinaryUsageAllowed'] and 0 <= age.total_seconds() <= 120
    assert all(w is None or w['remainingPercent'] > 10 for w in (q['primary'],q['secondary']))
    source = begin['values']['source']
    build, scope = h.evidence('41504'), h.evidence('41506')
    v, verified = h.read(build), h.read(scope)
    assert v['source'] == verified['source'] == h.git('rev-parse','HEAD').decode().strip() == source
    assert v['compileScopeVerified'] and verified['actualExit'] == 0
    work = Path(v['cwd'])
    target = work / 'target/classes'
    allowed = v['physical']
    assert {p.relative_to(target).as_posix():h.pin(p)['sha256'] for p in target.rglob('*.class')} == allowed
    assert allowed == verified['exactTargets']
    permitted_aux = verified['exactAuxiliaries']
    assert all(h.pin(Path(name))['sha256'] == metadata['sha256'] for name, metadata in permitted_aux.items())
    paths = {}
    for name, checksum in v['sourceScope'].items():
        p = work / 'src/main/java' / name.split('/src/main/java/',1)[1]
        assert h.pin(p)['sha256'] == checksum and h.pin(Path(name))['sha256'] == checksum
        paths[str(p)]=name
    assert len(paths) == 30
    java_runtime = h.TOOLS / 'jdk-25.0.4/lib/jrt-fs.jar'
    inputs = [str(java_runtime),str(target),*permitted_aux]
    rules = h.ROOT / 'tools/quality/static/pmd.xml'
    assert rules.read_bytes() == h.git('show',f'{source}:tools/quality/static/pmd.xml')
    prior = h.read(h.evidence('41310'))['stages']['pmd']['command']
    assert prior[3:6] == ['net.sourceforge.pmd.cli.PmdCli','check','--file-list']
    assert all(Path(s).is_relative_to(h.TOOLS) for s in prior[2].split(os.pathsep))
    home = h.ROOT.parent / 'pgpt-runs/PG379' / RUN
    home.mkdir(mode=0o700)
    listing, output = home/'inputs.txt', home/'pmd.xml'
    listing.write_text('\n'.join(sorted(paths))+'\n')
    cmd = [*prior[:6],str(listing),'--rulesets',str(rules),'--use-version','java-25','--aux-classpath',
           os.pathsep.join(inputs),'--no-cache','--format','xml','--report-file',str(output)]
    receipt = dict(source=source, core=v['core'], run=RUN, inspectedInputs=paths,
                   exactScopeReceipt=h.pin(scope), buildProof=h.pin(build), rules=h.pin(rules),
                   jvmRuntime=h.pin(java_runtime), command=cmd,beganAtUTC=h.now())
    h.write(home/'begin.json',receipt)
    r = subprocess.run(cmd,capture_output=True,timeout=150)
    (home/'stdout').write_bytes(r.stdout)
    (home/'stderr').write_bytes(r.stderr)
    tree = ET.parse(output).getroot()
    findings = []
    for node in tree:
        if local(node.tag) != 'file':
            continue
        name = paths[node.get('name')]
        for item in node:
            if local(item.tag) == 'violation':
                findings.append(dict(path=name,rule=item.get('rule'),begin=int(item.get('beginline')),
                                     end=int(item.get('endline')),priority=int(item.get('priority'))))
    errors = sum(local(x.tag) in ('error','configerror') for x in tree.iter())
    suppressed = sum(local(x.tag) == 'suppressedviolation' for x in tree.iter())
    out = h.OPS / RUN
    out.mkdir()
    h.write(out/'manifest.json',dict(**receipt,actualExit=r.returncode,observedFindings=len(findings),findingSites=findings,
        processingErrors=errors, manualSuppressionInserted=0, reportedExistingSuppressions=suppressed,
        originalXml=h.pin(output), stdout=h.pin(home/'stdout'), stderr=h.pin(home/'stderr'),
        newTestExecutions=0, whole451=False, formalAcceptanceId=None,terminalAtUTC=h.now()))
    print('PMD exit',r.returncode,'raw',len(findings),'errors',errors)


if __name__ == '__main__':
    main()
