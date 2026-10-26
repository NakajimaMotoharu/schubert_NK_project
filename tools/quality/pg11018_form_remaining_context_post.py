"""Independent original-raw/current-source/compiled-Test ownership-context validation; no Product replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from classfile_code_metadata import decode

SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
OUT = data.BASE/'PG11018-form-remaining-context-post-v1'


def contract(rows,original,hashes,xml_rows):
    if len(rows) != 12 or len({r['id'] for r in rows}) != 12:
        raise ValueError('twelve unique original diagnostics')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != old['path'] or row['sourceSha256'] != hashes[row['path']]:
            raise ValueError('current exact source and original diagnostic path')
        if row['originalRowSha256'] != old['rowSha256'] or row['rule'] != old['rule']:
            raise ValueError('immutable raw rule/row identity')
        if (row['path'],row['attributes']) not in xml_rows:
            raise ValueError('actual current coordinates, not historical positions')
        basis = row['basis']
        if row['rule'] == 'CloseResource':
            if basis['kind'] != 'OWNERSHIP_TRANSFER_TO_TEST_AUTOCLOSEABLE_RECORD' or basis['factory'] not in (
                'UserStatusForm','UserRoleForm','PasswordResetForm','UserUnlockForm'):
                raise ValueError('one of four concrete form owners')
        elif row['rule'] == 'DoNotUseThreads':
            if basis['kind'] != 'FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME' or basis['workers'] != 8 or basis['tasks'] != 100:
                raise ValueError('ordinary finite Test worker context only')
        else:
            raise ValueError('no rule-generalized exemption')
        if row['status'] != 'CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or row['currentWholeCaseRefs'] or row['oldRuntimeReassigned']:
            raise ValueError('not full-current/old-runtime acceptance')
        if not row['rawWarningRetained'] or row['productTestsExecuted'] != 0 or row['coverage'] is not None or row['ptExecutionExempt']:
            raise ValueError('no suppression, invented execution or coverage')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG11016-form-remaining-context-v1/manifest.json'
    primary = data.read_checked(path,'0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51')
    rows = data.read_checked(path.parent/'contexts.json',primary['contextsSha256'])
    normal = data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json',
        '5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    proof_path = data.BASE/'PG11014-form-close-assert-post-v1/manifest.json'
    proof = data.read_checked(proof_path,'c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa')
    measurement = data.read_checked(proof_path.parent/'measurement.json',proof['measurementSha256'])
    original_rows = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in original_rows}
    hashes = normal['begin']['inputHashes']
    assert normal['source'] == proof['source'] == primary['source'] == SOURCE and primary['actualExit'] == proof['actualExit'] == 0
    static_path = data.BASE/'PG11012-form-close-assert-static-v1/manifest.json'
    static = data.read_checked(static_path,'d642c529b96c8cac73372108e5ea6423cf829e5ea8923badae39fffe04be5df0')
    raw = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd']['sha256']
    xml_rows = [(str(Path(file.get('name')).relative_to(data.ROOT)),dict(node.attrib)) for file in ET.fromstring(raw)
        if file.tag.rpartition('}')[2] == 'file' for node in file if node.tag.rpartition('}')[2] == 'violation']
    assert len(xml_rows) == 12
    contract(rows,original,hashes,xml_rows)
    factories = {r['basis']['factory'] for r in rows if r['rule'] == 'CloseResource'}
    assert len(factories) == 4
    prefix = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/'
    for factory in factories:
        p = prefix+factory+'.java'
        assert data.sha((data.ROOT/p).read_bytes()) == hashes[p]
        unit = measurement['selectedFormMain']['dev/codex/schubert/nk/web/form/'+factory+'.class']
        assert unit['counters']['METHOD']['missed'] == 0 and unit['counters']['METHOD']['covered'] == 8
    test_root = Path(normal['jars']['web']['path']).parent/'test-classes/dev/codex/schubert/nk/web/form'
    record = decode((test_root/'UserMutationFormTest$Form.class').read_bytes(),'dev/codex/schubert/nk/web/form/UserMutationFormTest$Form.class')
    assert record['sourceFile'] == 'UserMutationFormTest.java'
    # The source text has no conditional close policy: the record delegates to its captured closer.
    source_path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/UserMutationFormTest.java'
    text = (data.ROOT/source_path).read_text()
    assert 'public void close() {\n      closer.run();\n    }' in text
    assert text.count('yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);') == 4
    assert data.sha(text.encode()) == hashes[source_path]
    bads = [rows[:-1],rows+[rows[0]]]
    for key,value in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('productTestsExecuted',40),
                      ('coverage',100),('ptExecutionExempt',True),('rawWarningRetained',False)]:
        bad = copy.deepcopy(rows)
        bad[0][key] = value
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,original,hashes,xml_rows)
        except ValueError:
            pass
        else:
            raise AssertionError('invented source/runtime/suppression accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),
        selectedMainProofSha256=data.sha(proof_path.read_bytes()),compiledRecordSourceFile=record['sourceFile'],
        sourceLocalContexts=12,rawStaticGate=1,wholeF03Accepted=False,whole451Accepted=False,
        productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
