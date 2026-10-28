"""Independent complete class/ABI/static binding for PG-only constants, never load Product."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts
from pg13131_main_literal_inverse import inverse, negative
import pg9666_pagination_static as runner

SOURCE = '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13138-main-literal-post-v1'
OUT = data.BASE/'PG13138-main-literal-post-v1'
ROOTS = {
    'batch':'dev/codex/schubert/nk/batch/file/TransferCleanup',
    'bootstrap':'dev/codex/schubert/nk/bootstrap/LinuxSystemdSession',
}
DECLARATIONS = {
    'batch':'private static final int MINIMUM_SUPPORTED_DATE_YEAR = 1;',
    'bootstrap':'private static final java.lang.String LIBC_FREE_SYMBOL = "free";',
}

def shape(model):
    value = copy.deepcopy(model)
    for method in value['methods']:method.pop('codeLength')
    return value

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json','ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823')
    old = data.read_checked(data.BASE/'PG13106-snapshot-corrected-six-compile-v1/manifest.json','0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7')
    s = data.read_checked(data.BASE/'PG13136-main-literal-static-v1/manifest.json','363f2e0fbda83bd9fd37ce57236e4197f3205dfa4b59f98f9e4a2395f2a8f479')
    p = data.read_checked(data.BASE/'PG13132-main-literal-preflight-v1/manifest.json','4367bdd95cd9f8f503855250edb1b9104ad2bd2edf146018912596973ed8f9c0')
    om = data.read_checked(data.BASE/'PG13130-main-literal-originals-v1/manifest.json','1ae8f6627fa5a7092106d5659601102a556915061e8c4950928086706e906c34')
    originals = data.read_checked(data.BASE/'PG13130-main-literal-originals-v1/originals.json',om['originalsSha256'])
    assert n['source'] == s['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == s['actualExit'] == 0
    assert s['spotbugsSixExit'] == 0 and s['rawStatic'] == 14 and s['rawStaticGateExit'] == 1
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert {path for path in n['begin']['inputHashes'] if n['begin']['inputHashes'][path] != old['begin']['inputHashes'][path]} == set(p['candidateSourceHashes'])
    for row in originals['sources']:
        text = (data.ROOT/row['path']).read_text()
        assert inverse(row['path'],row['text'],text) == p['originalTokenInverses'][row['path']]
        assert negative(row['path'],row['text'],text) == p['negativeVectors'][row['path']] == 6
    a,b = jar_classes(old),jar_classes(n);assert set(a) == set(b) and len(a) == 1843
    changed = {key for key in a if a[key] != b[key]}
    closure = {key for key in a if key[0] in ROOTS and (key[1] == ROOTS[key[0]]+'.class' or key[1].startswith(ROOTS[key[0]]+'$'))}
    assert changed and changed <= closure
    old_tests,new_tests = test_classes(old),test_classes(n)
    assert old_tests == new_tests and len(new_tests) == 1973
    metadata = []
    for role,entry in sorted(closure):
        with zipfile.ZipFile(old['jars'][role]['path']) as archive:x = parts(archive.read(entry),entry)
        with zipfile.ZipFile(n['jars'][role]['path']) as archive:y = parts(archive.read(entry),entry)
        expected = shape(x['model'])
        if entry == ROOTS[role]+'.class':expected['fields'] += 1
        assert shape(y['model']) == expected
        assert x['model']['sourceFile'] == y['model']['sourceFile'] == Path(ROOTS[role]).name+'.java'
        metadata.append(dict(module=role,entry=entry,byteChanged=(role,entry) in changed,
            oldFields=x['model']['fields'],newFields=y['model']['fields'],methodShapesUnchanged=True,
            rawCodeRepresentationEqual=x['rawCodeRepresentationSha256'] == y['rawCodeRepresentationSha256'],
            debugTablesEqual=x['debugTablesSha256'] == y['debugTablesSha256'],
            oldClassSha256=a[(role,entry)],newClassSha256=b[(role,entry)]))
    SLOT.mkdir();runner.SLOT = SLOT;stages = [];abi = {}
    javap = runner.TC/'jdk-25.0.4/bin/javap';javap_sha = data.sha(javap.read_bytes())
    for role,root in ROOTS.items():
        outputs = []
        for label,normal in [('old',old),('new',n)]:
            stage = runner.step(role+'-'+label+'-metadata',[str(javap),'-p','-constants','-s','-classpath',normal['jars'][role]['path'],root.replace('/','.')],SLOT,timeout=120)
            assert stage['actualExit'] == 0 and not stage['timedOut'];stages.append(stage)
            outputs.append((SLOT/(role+'-'+label+'-metadata.stdout')).read_text())
        lines = outputs[1].splitlines();matches = [line for line in lines if line.strip() == DECLARATIONS[role]]
        assert len(matches) == 1 and '\n'.join(line for line in lines if line not in matches)+'\n' == outputs[0]
        abi[role] = dict(newPrivateConstant=DECLARATIONS[role],allOtherPrivatePublicMetadataIdentical=True,
            oldOutputSha256=data.sha(outputs[0].encode()),newOutputSha256=data.sha(outputs[1].encode()))
    assert data.sha(javap.read_bytes()) == javap_sha
    sb = {}
    for role,item in n['jars'].items():
        path = Path(item['path']).parent/'spotbugsXml.xml';raw = path.read_bytes()
        assert not list(ET.fromstring(raw).iter('BugInstance'))
        sb[role] = data.sha(raw)
    assert jar_classes(n) == b and test_classes(n) == new_tests
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        allMainPhysical=len(a),changedMainPhysical=len(changed),otherMainUnchanged=len(a)-len(changed),
        sourceFileClosureClasses=len(closure),classMetadata=metadata,allTestPhysicalUnchanged=len(new_tests),
        sourceInputsOnlyTwoChanged=True,privateMetadata=abi,javapSha256=javap_sha,spotbugsSixReports=sb,
        rawStatic=14,rawStaticGateExit=1,removedOriginalFindingIds=['PMD-02953','PMD-06175'],
        tokenInverseNegativeVectors=12,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',
        coverageStatus='NOT_MEASURED',oldPtQualificationTransferred=False,rawCodeHashIsNotSemanticProof=True,
        newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
