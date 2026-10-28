"""Independent complete physical/ABI check of Test-only constants; no target loading or execution."""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts
from pg13190_systemd_test_literal_originals import PATH, OLD_SHA
from pg13191_systemd_test_literal_inverse import inverse, negative, CONSTANTS
from pg13139_private_constant_metadata import remove_constant, selftest
import pg9666_pagination_static as runner

SOURCE = '41359340de234b8bea7578d957bcbf4df6ab951f'
OUT = data.BASE/'PG13198-systemd-test-literal-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13198-systemd-test-literal-post-v1'
ROOT = 'dev/codex/schubert/nk/bootstrap/LinuxSystemdSessionTest'

def shape(model):
    result = copy.deepcopy(model)
    for method in result['methods']:method.pop('codeLength')
    return result

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    field_vectors = selftest()
    n = data.read_checked(data.BASE/'PG13194-systemd-test-literal-six-compile-v1/manifest.json','6c6809515a4ae056dad337e44b5ffd8e26b617e0292e88df7082b3ddcddea1b9')
    old = data.read_checked(data.BASE/'PG13176-numeric-ceiling-six-compile-v1/manifest.json','ba6cbaa31b2d244115de5665d30142d3b067da21625a01af415b1f002fbe940f')
    s = data.read_checked(data.BASE/'PG13196-systemd-test-literal-static-v1/manifest.json','34746d45558149ae8cf2eb13d460628c7d518b6c8b13e0c9770afcf58028a253')
    p = data.read_checked(data.BASE/'PG13192-systemd-test-literal-preflight-v1/manifest.json','1a7db1f6a6db5b41a8c61119b98825cd1cce173fa6eab50c050f91557e6066f1')
    om = data.read_checked(data.BASE/'PG13190-systemd-test-literal-originals-v1/manifest.json','9159076b27e5b090f8aa550402456d51d90daeb5790d84836fe74f113309457b')
    original = data.read_checked(data.BASE/'PG13190-systemd-test-literal-originals-v1/original.json',om['originalSha256'])
    assert data.sha(original['text'].encode()) == old['begin']['inputHashes'][PATH] == OLD_SHA
    assert n['source'] == s['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == s['actualExit'] == 0
    assert s['normalManifestSha256'] == data.sha((data.BASE/'PG13194-systemd-test-literal-six-compile-v1/manifest.json').read_bytes())
    assert s['rawStatic'] == 19 and s['rawStaticGateExit'] == 1 and s['spotbugsSixExit'] == 0
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert n['begin']['inputHashes'].keys() == old['begin']['inputHashes'].keys()
    assert {path for path in n['begin']['inputHashes'] if n['begin']['inputHashes'][path] != old['begin']['inputHashes'][path]} == {PATH}
    current = (data.ROOT/PATH).read_text()
    assert inverse(original['text'],current) == p['originalTokenInverse'] and negative(original['text'],current) == p['negativeVectors'] == 24
    before,after = jar_classes(old),jar_classes(n);assert before == after and len(after) == 1843
    a,b = test_classes(old),test_classes(n);assert a.keys() == b.keys() and len(b) == 1974
    closure = {key for key in a if key[0] == 'bootstrap' and (key[1] == ROOT+'.class' or key[1].startswith(ROOT+'$'))}
    changed = {key for key in a if a[key] != b[key]};assert changed and changed <= closure
    metadata = []
    for role,entry in sorted(closure):
        files = [Path(normal['jars'][role]['path']).parent/'test-classes'/entry for normal in [old,n]]
        x,y = [parts(file.read_bytes(),entry) for file in files]
        expected = shape(x['model'])
        if entry == ROOT+'.class':expected['fields'] += len(CONSTANTS)
        assert shape(y['model']) == expected and x['model']['sourceFile'] == y['model']['sourceFile'] == 'LinuxSystemdSessionTest.java'
        metadata.append(dict(module=role,entry=entry,byteChanged=(role,entry) in changed,oldClassSha256=a[(role,entry)],newClassSha256=b[(role,entry)],
            oldFields=x['model']['fields'],newFields=y['model']['fields'],methodShapesUnchanged=True,
            rawCodeRepresentationEqual=x['rawCodeRepresentationSha256'] == y['rawCodeRepresentationSha256'],
            debugTablesEqual=x['debugTablesSha256'] == y['debugTablesSha256']))
    SLOT.mkdir();runner.SLOT = SLOT;javap = runner.TC/'jdk-25.0.4/bin/javap';javap_hash = data.sha(javap.read_bytes());outputs = [];stages = []
    for label,normal in [('old',old),('new',n)]:
        cp = str(Path(normal['jars']['bootstrap']['path']).parent/'test-classes')
        stage = runner.step(label+'-metadata',[str(javap),'-p','-constants','-s','-classpath',cp,ROOT.replace('/','.')],SLOT,timeout=120)
        assert stage['actualExit'] == 0 and not stage['timedOut'];stages.append(stage)
        outputs.append((SLOT/(label+'-metadata.stdout')).read_text())
    stripped = outputs[1]
    for name,value in CONSTANTS.items():
        stripped = remove_constant(stripped,'private static final java.lang.String '+name+' = '+json.dumps(value)+';','Ljava/lang/String;')
    assert stripped == outputs[0] and data.sha(javap.read_bytes()) == javap_hash
    sb = {}
    for role,item in n['jars'].items():
        path = Path(item['path']).parent/'spotbugsXml.xml';raw = path.read_bytes();assert not list(ET.fromstring(raw).iter('BugInstance'));sb[role] = data.sha(raw)
    assert jar_classes(n) == after and test_classes(n) == b
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        inputManifestHashes={name:data.sha((data.BASE/name/'manifest.json').read_bytes()) for name in ['PG13194-systemd-test-literal-six-compile-v1','PG13196-systemd-test-literal-static-v1']},
        allMainPhysicalUnchanged=len(after),previousTestPhysical=len(a),currentTestPhysical=len(b),changedTestPhysical=len(changed),oldTestPhysicalUnchanged=len(a)-len(changed),newTestPhysical=0,
        sourceFileClosureClasses=len(closure),classMetadata=metadata,privateConstantsAdded=len(CONSTANTS),allOtherPrivatePublicMetadataUnchanged=True,
        javapSha256=javap_hash,javapOutputHashes={label:data.sha(value.encode()) for label,value in zip(['old','new'],outputs)},metadataFieldVectors=field_vectors,
        originalTokenInverse=p['originalTokenInverse'],tokenInverseNegativeVectors=24,removedFindingIds=p['removedFindingIds'],rawStatic=19,rawStaticGateExit=1,spotbugsSixReports=sb,
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',oldPtQualificationTransferred=False,rawCodeHashIsNotSemanticProof=True,
        newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
