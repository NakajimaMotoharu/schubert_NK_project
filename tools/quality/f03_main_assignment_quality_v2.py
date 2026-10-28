"""Main statement source inverse, complete byte scope and all closure member metadata; no target run."""
import copy
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import out, prior_normal, original_value
from f03_main_assignment_final_sources import inverse, negative
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts, selftest
import pg9666_pagination_static as runner

def shape(model):
    result = copy.deepcopy(model)
    for method in result['methods']:
        method.pop('codeLength')
    return result

def post(cfg,source,normal_pin,static_pin):
    invocation = capture(__file__)
    target = out(cfg,cfg.POST_NUMBER)
    slot = data.ROOT.parent/'pgpt-runs/PG379'/target.name.lower()
    assert not target.exists() and not slot.exists()
    normal = data.read_checked(out(cfg,cfg.NORMAL_NUMBER)/'manifest.json',normal_pin)
    static = data.read_checked(out(cfg,cfg.STATIC_NUMBER)/'manifest.json',static_pin)
    preflight = data.read_checked(out(cfg,cfg.PREFLIGHT_NUMBER)/'manifest.json','36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda')
    old = prior_normal(cfg)
    assert normal['source'] == static['source'] == source
    assert normal['actualExit'] == normal['testsExecuted'] == static['actualExit'] == static['spotbugsSixExit'] == 0
    assert static['normalManifestSha256'] == normal_pin and static['preflightManifestSha256'] == '36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda'
    assert static['rawStatic'] == preflight['rawStatic'] == 14 and static['rawStaticGateExit'] == 1
    hashes = normal['begin']['inputHashes']
    assert hashes.keys() == old['begin']['inputHashes'].keys()
    assert {path for path in hashes if hashes[path] != old['begin']['inputHashes'][path]} == set(cfg.PATHS)
    assert all(data.sha((data.ROOT/path).read_bytes()) == pin for path,pin in hashes.items())
    original = original_value(cfg)
    for row in original['sources']:
        text = (data.ROOT/row['path']).read_text()
        assert inverse(row['text'],text,row['mapping']) == preflight['originalTokenInverses'][row['path']]
        assert negative(row['text'],text,row['mapping']) == preflight['negativeVectors'][row['path']] == 5
    before,after = jar_classes(old),jar_classes(normal)
    assert before.keys() == after.keys() and len(before) == len(after) == 1843
    old_tests,new_tests = test_classes(old),test_classes(normal)
    assert old_tests == new_tests and len(new_tests) == 1978
    roots = {(path.split('/')[1].removeprefix('schubert-nk-'),path.split('/src/main/java/')[1][:-5]) for path in cfg.PATHS}
    closure = {key for key in before if any(key[0] == role and (key[1] == root+'.class' or key[1].startswith(root+'$')) for role,root in roots)}
    changed = {key for key in before if before[key] != after[key]}
    assert changed and changed <= closure
    metadata = []
    for module in sorted({role for role,_ in closure}):
        with zipfile.ZipFile(old['jars'][module]['path']) as a,zipfile.ZipFile(normal['jars'][module]['path']) as b:
            for role,entry in sorted(key for key in closure if key[0] == module):
                x,y = parts(a.read(entry),entry),parts(b.read(entry),entry)
                assert shape(x['model']) == shape(y['model'])
                metadata.append(dict(module=role,entry=entry,byteChanged=(role,entry) in changed,
                    oldClassSha256=before[(role,entry)],newClassSha256=after[(role,entry)],
                    allMethodStructuresUnchanged=True,rawCodeRepresentationEqual=x['rawCodeRepresentationSha256'] == y['rawCodeRepresentationSha256'],
                    debugTablesEqual=x['debugTablesSha256'] == y['debugTablesSha256']))
    slot.mkdir()
    runner.SLOT = slot
    javap = runner.TC/'jdk-25.0.4/bin/javap'
    tool_pin = data.sha(javap.read_bytes())
    outputs,stages = {},[]
    for module in sorted({role for role,_ in closure}):
        names = [entry[:-6].replace('/','.') for role,entry in sorted(closure) if role == module]
        pair = []
        for label,value in [('before',old),('after',normal)]:
            name = module+'-'+label+'-all-closure-members'
            result = runner.step(name,[str(javap),'-p','-constants','-s','-classpath',value['jars'][module]['path'],*names],slot,timeout=120)
            assert result['actualExit'] == 0 and not result['timedOut']
            stages.append(result)
            pair.append((slot/(name+'.stdout')).read_bytes())
        assert pair[0] == pair[1]
        outputs[module] = [data.sha(value) for value in pair]
    assert data.sha(javap.read_bytes()) == tool_pin
    assert jar_classes(normal) == after and test_classes(normal) == new_tests
    assert all(data.sha((data.ROOT/path).read_bytes()) == pin for path,pin in hashes.items())
    verify(invocation)
    target.mkdir()
    data.write(target/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,
        normalManifestSha256=normal_pin,staticManifestSha256=static_pin,
        preflightManifestSha256='36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda',
        allMainPhysical=1843,changedMainPhysical=len(changed),unchangedMainPhysical=1843-len(changed),
        sourceFileClosureClasses=len(closure),classMetadata=metadata,allClosureMembersUnchanged=True,
        memberOutputsSha256=outputs,javapSha256=tool_pin,stages=stages,
        oldTestPhysical=1978,currentTestPhysical=1978,allTestPhysicalBytesUnchanged=True,newPhysicalClasses=0,
        originalTokenInverses=preflight['originalTokenInverses'],tokenNegativeVectors=20,metadataDecoderVectors=selftest(),
        rawCodeHashIsNotSemanticProof=True,removedFindingIds=preflight['removedFindingIds'],
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',
        oldPtQualificationTransferred=False,newAccepted=0,whole451Accepted=False,formalUpdated=False,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))
