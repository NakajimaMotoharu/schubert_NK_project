"""Independent before/after naming failure closure over all current input Java; no target execution."""
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG13495-positioned-name-rollout-post-v1'


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13486-positioned-current-literal-v1/manifest.json','7c2d971b10807387a897132984dc14472936ce6e65e4a75e8ba519f4644fff65')
    proof = data.read_checked(data.BASE/'PG13490-positioned-current-literal-v1/manifest.json','560cc3a4c7631f289e53268e3a044c99ba660b58d9f0a454c17f71bd0b69df21')
    recovered = data.read_checked(data.BASE/'PG13483-positioned-current-literal-v1/manifest.json','84af6350dc7965e2da44b92d17f8a5e19873d95ce95ff5fd4ddf1ac46848ed56')
    after = data.read_checked(data.BASE/'PG13485-positioned-current-literal-v1/manifest.json','cabd95bdc7433493b4765cdde40845c4ea5c4d5ef2eda0004bc7338771cd045d')
    assert normal['source'] == proof['source'] == 'ff8149dd27decbe683b48d1cbb5f2cb59ecca83a'
    assert normal['actualExit'] == proof['actualExit'] == after['actualExit'] == 0 and normal['testsExecuted'] == proof['productTestsExecuted'] == 0
    assert recovered['originalBeforeTextRecaptured'] is False and len(recovered['renamedConstants']) == 2
    old_names = {row['oldName'] for row in recovered['renamedConstants']}
    new_names = {row['newName'] for row in recovered['renamedConstants']}
    names,files = set(),0
    for path,sha in normal['begin']['inputHashes'].items():
        raw = (data.ROOT/path).read_bytes()
        assert data.sha(raw) == sha
        if path.endswith('.java'):
            files += 1
            names.update(match.group() for match in LEX.finditer(raw.decode()) if match.group().startswith('FIXTURE_'))
    assert new_names <= names and not old_names & names
    assert all(re.fullmatch(r'[A-Z][A-Z0-9]*(_[A-Z0-9]+)*',name) for name in names)
    failed = data.ROOT.parent/'pgpt-runs/PG379/pg13484-positioned-current-literal-v1'
    raw = (failed/'checkstyle.xml').read_bytes()
    assert data.sha(raw) == 'a33ba6239d673b2205f39fa9e72ef88fea4da39333f65d43b950e7c0bdb6874d'
    errors = [node for node in ET.fromstring(raw).iter('error')]
    assert len(errors) == 2 and all(node.get('source').endswith('.ConstantNameCheck') for node in errors)
    assert all(any(name in node.get('message') for node in errors) for name in old_names)
    assert after['stages']['checkstyle']['actualExit'] == 0 and len(after['removedFindingIds']) == 91
    current_xml = data.BASE/'PG13485-positioned-current-literal-v1/checkstyle.xml'
    assert data.sha(current_xml.read_bytes()) == after['reports']['checkstyle'] and not list(ET.parse(current_xml).getroot().iter('error'))
    assert proof['privateConstantsAdded'] == 91 and proof['allMainPhysicalUnchanged'] == 1843 and proof['currentTestPhysical'] == 1978
    verify(invocation)
    OUT.mkdir()
    with (OUT/'original-failed-checkstyle.xml').open('xb') as stream:
        stream.write(raw)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,normalManifestSha256='7c2d971b10807387a897132984dc14472936ce6e65e4a75e8ba519f4644fff65',
        originalFailureActualExit=1,originalCheckstyleExit=2,originalFailedCheckstyleSha256=data.sha(raw),currentCheckstyleExit=0,currentCheckstyleSha256=after['reports']['checkstyle'],
        allCurrentInputJavaFiles=files,uniqueFixtureIdentifiers=len(names),invalidCurrentFixtureNames=[],repairedOldNames=sorted(old_names),verifiedNewNames=sorted(new_names),
        sourceSemanticValuesChanged=False,originalBeforeTextRecaptured=False,onlyGeneratedNameRepairCount=2,allSelectedConstants=91,normalMainUnchanged=1843,testPhysical=1978,
        immutableHistoricalSelectorsNotRewritten=True,newNamesRequireV2FinalPatternGuard=True,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
