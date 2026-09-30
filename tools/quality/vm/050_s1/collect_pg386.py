"""PG386 full-six sanitized provisional capture; native/100% acceptance remains separate."""
import importlib.util
import subprocess
import pathlib
import xml.etree.ElementTree as ET

root=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
spec=importlib.util.spec_from_file_location('capture',root/'tools/quality/050_collect_pg343_six.py')
capture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
source='d49a3a9fb' # Resolve and freeze exact commit, never retarget a previous result.
head=subprocess.check_output(['git','rev-parse',source],cwd=root,text=True).strip()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==head
subprocess.run(['git','diff','--exit-code',head,'--','src','tools','pom.xml'],cwd=root,check=True)
log=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg386-six-provisional.log')
raw=log.read_text()
assert 'BUILD SUCCESS' in raw and raw.count('BugInstance size is 0')==6
assert 'do not match with execution data' not in raw
out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG386-known-backup-failure'
assert not out.exists()
modules,coverage={},{}
for name,expected in [('protocol',80),('storage',149),('bootstrap',182),('api',756),('web',565),('batch',812)]:
    target=root/f'src/schubert-nk-{name}/target'
    reports=sorted((target/'surefire-reports').glob('TEST-*.xml'))
    folder=out/'junit'/name
    folder.mkdir(parents=True)
    count=0
    for report in reports:
        suite=ET.parse(report).getroot()
        assert all(int(suite.get(k))==0 for k in ('failures','errors','skipped'))
        assert len(suite.findall('testcase'))==int(suite.get('tests'))
        safe=ET.Element('testsuite',{k:suite.get(k) for k in ('name','tests','failures','errors','skipped','time')})
        for case in suite.findall('testcase'):
            assert all(child.tag in ('system-out','system-err') for child in case)
            ET.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
        ET.indent(safe)
        ET.ElementTree(safe).write(folder/report.name,encoding='utf-8',xml_declaration=True)
        count+=int(suite.get('tests'))
    assert count==expected
    modules[name]={'tests':count,'suites':len(reports),'failures':0,'errors':0,'skipped':0}
    coverage[name]=capture.counters(ET.parse(target/'site/jacoco/jacoco.xml').getroot())
    bugs=ET.parse(target/'spotbugsXml.xml').getroot()
    assert not bugs.findall('BugInstance') and int(bugs.find('Errors').get('errors'))==0
(out/'coverage').mkdir()
capture.emit(out/'coverage/all-modules.json',coverage)
manifest={'id':'PG386-known-backup-failure','formal':False,'sourceCommit':head,'branch':'dev-foundation',
 'environment':'Linux UID1000/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0',
 'command':'fixed JDK/Node/m2; Production6 clean test spotbugs:check jacoco:report jar:jar runtime dependency copy/list','exitCode':0,
 'executionTime':next(line.split('Finished at: ',1)[1] for line in raw.splitlines() if 'Finished at: ' in line),
 'input':'279 known worker failure completion and existing six regression; native failed/restore/positive captured separately',
 'expected':'all F/E/S0/static0; known normal nonzero failure records both COMMAND_FAILURE under owner; no secret; no formal/native claim',
 'actual':{'tests':sum(m['tests'] for m in modules.values()),'suites':sum(m['suites'] for m in modules.values()),'staticFindings':0,'externalMorningAccepted':False,'backupPositiveNativeRoundtrip':True},
 'modules':modules,'coverage':coverage,'bugs':['BUG-325'],'ssc':['SSC-108','SSC-109','SSC-110','SSC-111','SSC-112','SSC-113','SSC-114','SSC-115'],
 'log':{'path':str(log),'sha256':capture.sha(log)},
 'limitations':['Coverage below100%, native unresolved; not formal53scope','Actual normal FAILED and restored positive proved separately; complete Morning/timeout/Expiry/issuer/APIWeb/CHR not accepted','BUG325 subsequent cleanup/issuer and YKT whole lateral targets remain open','No mixed-source result'],
 'redaction':'JUnit properties/raw diagnostics/stdout/stderr omitted; no credential/password/token/session/dump/private key'}
manifest['files']=[{'path':str(p.relative_to(root)),'sha256':capture.sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
capture.emit(out/'manifest.json',manifest)
print({'source':head,'tests':manifest['actual']['tests'],'coverage':coverage,'manifestSha256':capture.sha(out/'manifest.json')})
