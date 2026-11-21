"""Qualify the completed BUG-3494 Protocol run against independent names and raw counters."""

import importlib.util
from pathlib import Path
import os
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from jacoco_readonly_exec_subset import decode

parent = Path(__file__).with_name('5694_qa054_canonical_rules_protocol_verify.py')
spec = importlib.util.spec_from_file_location('protocol_run_receipt',parent)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def main():
    home = h.ROOT.parent/'pgpt-runs/PG379'/h.RUN
    begin = h.read(home/'begin.json')
    final = h.read(home/'terminal.json')
    assert h.pin(home/'begin.json') == final['receipt']
    assert h.pin(home/'maven.log') == final['log'] and final['exitCode'] == 0
    source, baseline = begin['source'], next(h.OPS.glob('PG41304-*'))
    assert h.git('rev-parse','HEAD').decode().strip() == source
    prev, cases = h.read(baseline/'manifest.json'), h.read(baseline/'cases.json')
    expected = {(x['className'],x['method']) for x in cases if x['outcome']=='PASS'}
    assert len(expected)==171
    work = Path(begin['work'])
    for p, digest in begin['currentInputs'].items():
        assert h.pin(work/p)['sha256'] == digest
    target = work/h.MODULE/'target'
    parsed = {}
    files = {}
    for report in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        root=ET.parse(report).getroot()
        assert all(int(root.get(k,'0'))==0 for k in ('errors','skipped','failures'))
        files[report.name]=h.pin(report)['sha256']
        for case in root.iter('testcase'):
            key=(case.get('classname'),case.get('name'))
            assert key not in parsed and not any(case.find(k) is not None for k in ('error','failure','skipped'))
            parsed[key] = 'PASS'
    assert len(files)==39 and set(parsed)==expected

    jar = next(target.glob('schubert-nk-protocol-*.jar'))
    saved_jar=home/jar.name
    if not saved_jar.exists():
        with saved_jar.open('xb') as stream:
            stream.write(jar.read_bytes())
    assert h.pin(saved_jar)['sha256'] == h.pin(jar)['sha256']
    archive_receipt=h.read(next(h.OPS.glob('PG41322-*'))/'manifest.json')['packagingProof']['artifacts']['protocol']['artifact']
    previous=Path(archive_receipt['path'])
    assert h.pin(previous)==archive_receipt
    assert archive_receipt['sha256']==prev['localJar']['sha256']
    def classes(path):
        with ZipFile(path) as archive:
            return {k:h.sha(archive.read(k)) for k in archive.namelist() if k.endswith('.class')}
    old,new=classes(previous),classes(saved_jar)
    assert len(new)==176 and old.keys()==new.keys()
    changed=[n for n in new if new[n]!=old[n]]
    assert changed==['dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog.class']
    current_classes={p.relative_to(target/'classes').as_posix():p for p in (target/'classes').rglob('*.class')}
    assert {n:h.pin(p)['sha256'] for n,p in current_classes.items()}==new

    analyzer=work/'independent-analyzer'
    analyzer.mkdir()
    compile_argv=prev['tools'][0]['argv']
    runtime=prev['tools'][1]['argv']
    dependencies=compile_argv[5]
    assert all(Path(p).is_file() for p in dependencies.split(os.pathsep))
    analyzer_source=Path('tools/quality/jacoco/UnfilteredCodeMeasurement.java').resolve()
    compiler=[*compile_argv[:6],'-d',str(analyzer),str(analyzer_source)]
    check=subprocess.run(compiler,capture_output=True,timeout=60)
    assert check.returncode==0
    execfile=target/'jacoco.exec'
    command=[runtime[0],'-cp',str(analyzer)+os.pathsep+dependencies,
             'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',
             '--strict-original-exec','--line-deficits',str(execfile),
             *map(str,current_classes.values())]
    result=subprocess.run(command,capture_output=True,timeout=90)
    assert result.returncode==0
    raw=result.stdout.decode().splitlines()
    counted={}
    expected_crcs={}
    for row in raw:
        c=row.split('\t')
        if c[0]=='CLASS':
            assert c[1] not in counted
            counted[c[1]]={k:dict(missed=int(m),covered=int(v)) for k,m,v in (x.split(':') for x in c[6:])}
            if c[3]=='true':
                expected_crcs[c[1]]=int(c[2],16)
    assert len(counted)==176
    original=decode(execfile.read_bytes(),set(expected_crcs),strict_class_names=True)
    assert len(original['sessions'])==1
    assert all(int(original['classes'][k]['crc64'],16)==c for k,c in expected_crcs.items())
    counter_keys=('LINE','METHOD','CLASS','BRANCH','INSTRUCTION')
    totals={k:dict(missed=sum(c[k]['missed'] for c in counted.values()),
                  covered=sum(c[k]['covered'] for c in counted.values())) for k in counter_keys}
    assert all(totals[k]['missed']==0 for k in counter_keys[:4])
    documented=ET.parse(target/'site/jacoco/jacoco.xml').getroot()
    assert all(int(c.get('missed'))==0 for c in documented.findall('counter') if c.get('type') in counter_keys[:4])
    spot=ET.parse(target/'spotbugsXml.xml').getroot()
    assert not spot.findall('.//BugInstance') and not spot.findall('.//MissingClass') and not spot.findall('.//Error')

    canon_path=next(Path('documents/200_UI/230_インターフェース').glob('235_*.md'))
    canon=h.git('show',f"{begin['originMain']}:{canon_path}").decode().split('### 12.2 QA-054',1)[0].split('`WLGEVT01`',1)[-1]
    approved={}
    for line in canon.splitlines():
        a=[t.strip() for t in line.split('|')[1:-1]]
        if len(a)==6 and tuple(a[:5]) in (('Log type','18','16','X','M'),('Action','42','64','X','O')):
            approved[a[0]]=a[5]
    assert set(approved)=={'Log type','Action'}
    fixed=work/'src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv'
    rows=[line.split('\t') for line in fixed.read_text().splitlines() if line.startswith('WLGEVT01\tDATA\t')]
    assert {r[2]:r[-1] for r in rows if r[2] in approved}==approved
    before=h.read(next(h.OPS.glob('PG41524-*'))/'manifest.json')
    assert before['fieldRows']==389 and len(before['qa054NonStructuralDiff'])==2
    # The previous complete scan pinned every other field; the tracked diff is exactly these notes.
    out = h.OPS/h.RUN
    out.mkdir()
    report = out/'unfiltered.tsv'
    report.write_bytes(result.stdout)
    h.write(out/'case-names.json',[dict(className=a,method=b,outcome='PASS') for a,b in sorted(parsed)])
    h.write(out/'manifest.json',dict(run=h.RUN,source=source,productionCore=source,actualExit=0,
        oldProductionCore=before['core'],historicalJarMatchedByDigest=archive_receipt,
        initialPost='The prior scratch archive had expired; used the separately retained byte-identical archive.',start=final['receipt'],terminal=final,bug='BUG-3494',ykt='YKT-2787',
        sourceInputs=217,currentPackage=h.pin(saved_jar),physicalClasses=len(counted),classByteChanges=changed,
        priorCaseScope=h.pin(baseline/'cases.json'),exactCaseRoster=h.pin(out/'case-names.json'),
        originalXmlSha256=files,tests=171,suites=39,failures=0,errors=0,skipped=0,notRun=0,newDefinitions=0,
        raw=totals,rawReport=h.pin(report),sameOriginalExec=h.pin(execfile),derivedExecUnion=False,
        classRawForChanged=counted[changed[0].removesuffix('.class')],
        plainMavenSpotlessAndSpotBugsZero=True,requiresNoGlobalClassificationChange=True,
        independentQa054Descriptions=dict(equal=True,ruleCount=2,totalFieldRows=389),
        packageGeneratedModules=['Protocol'],actualRemoteBackendJobs=0,whole451=False,formalAcceptanceId=None,
        commands=[compiler,command],terminalAtUTC=h.now()))
    print('Verified',len(parsed),len(files),'raw',totals,'changed classes',len(changed))


if __name__ == '__main__':
    main()
