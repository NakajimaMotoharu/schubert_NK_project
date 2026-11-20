"""Independently close the bounded set of generic and normalized XML readers."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
from xml.etree import ElementTree as ET


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TOOL = Path(__file__).with_name('5609_scr012_count_underclaim.py')
QUALITY = Path('tools/quality')
ROWS = (
    ('pg2734_backup_published_qualification.py','vm/050_s1/Pg2732BackupPublishedLauncher.java'),
    ('pg2738_backup_retention_qualification.py','vm/050_s1/Pg2736BackupRetentionLauncher.java'),
    ('pg2742_backup_pending_qualification.py','vm/050_s1/Pg2740BackupPendingLauncher.java'),
    ('pg2752_db_backup_handoff_qualification.py','vm/050_s1/Pg2750BackupHandoffLauncher.java'),
    ('pg8845_typed_pool_binding_context.py','architecture/TypedPoolBindingJunitLauncher.java'),
    ('pg8857_api_caller_metric_context.py','architecture/ApiCallerMetricJunitLauncher.java'),
    ('pg8871_web_caller_metric_context.py','architecture/WebCallerMetricJunitLauncher.java'),
)


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def main():
    success = runpy.run_path(str(TOOL))['successful_case']
    passed = (
        ('empty', ''),
        ('stdout', '<system-out>public sample</system-out>'),
        ('stderr', '<system-err>public sample</system-err>'),
        ('both', '<system-out/><system-err/>'),
    )
    failed = (
        ('failure','<failure/>'),('error','<error/>'),('skip','<skipped/>'),
        ('flaky-failure','<flakyFailure/>'),('flaky-error','<flakyError/>'),
        ('rerun-failure','<rerunFailure/>'),('rerun-error','<rerunError/>'),
        ('unknown','<outcome/>'),('nested-result','<system-out><failure/></system-out>'),
        ('mixed','<system-err/><skipped/>'),
    )
    tests = []
    for expectation, samples in ((True,passed),(False,failed)):
        for item, value in samples:
            raw = '<testcase classname="fixture.Type" name="example">'+value+'</testcase>'
            got = success(ET.fromstring(raw))
            assert got is expectation
            tests.append(dict(case=item, expected=expectation, actual=got))
    old = []
    for index, (reader, generator) in enumerate(ROWS):
        checker = QUALITY/reader
        writer = QUALITY/generator
        java = writer.read_text()
        assert '"system-out"' not in java and '"system-err"' not in java
        assert 'not list(cases[' in checker.read_text()
        if index < 4:
            assert '(passed ? "" : "<failure' in java
            assert '</testcase></testsuite>' in java
            assert 'Files.writeString(Path.of(args[0]), xml' in java
        else:
            fragment = java.partition('xml.writeStartElement("testcase");')[2].partition('xml.writeEndElement();')[0]
            assert fragment.count('xml.writeEmptyElement') == 1
            assert 'if (!row.status().equals("SUCCESSFUL"))' in fragment
            assert '? "failure" : "skipped"' in fragment
            assert 'writeCharacters' not in fragment and 'writeStartElement' not in fragment
        old.append(dict(reader=pin(checker),generator=pin(writer),changeRequired=False,
                        proof='Bounded producer emits no children on success. Failure/skip representation remains subject to the original exact check.'))
    originals = []
    for run in ('PG41176','PG41178'):
        receipt, = OPS.glob(f'{run}-*/manifest.json')
        actual = json.loads(receipt.read_bytes())
        saved = actual['localOriginals'][-1]
        xml = Path(saved['path'])
        assert pin(xml) == saved and actual['xmlSha256'] == saved['sha256']
        suite = ET.fromstring(xml.read_bytes())
        case, = suite.findall('testcase')
        assert any(node.tag == 'system-out' for node in case) and success(case)
        originals.append(dict(receipt=pin(receipt),testId=actual['testId'],rawXmlSha256=saved['sha256'],
                              matches=True,productRepeated=False))
    output = OPS/'PG41180-g08-ykt2769-junit-case-shape-v1'
    output.mkdir()
    p = output/'manifest.json'
    with p.open('x') as f:
        json.dump(dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       testId='PT-OPS-JUNIT-CASE-SHAPE-001',changedTool=pin(TOOL),
                       toolTest=pin(Path(__file__)),literalCases=tests,
                       normalizedOldTools=old,previousRawLocalOriginals=originals,
                       oldProductExecutions=0,newProductExecutions=0,externalOperations=0,formalDelta=0,
                       entireProjectXmlGate=False),f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(p),len(tests),len(old),len(originals))


if __name__=='__main__':
    main()
