"""Rebind unchanged declaration names to current source/class bytes; no target execution."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '5e8255bcf8f309d05fb091cee2e9ad810b276c87'
NORMAL = ROOT.parent/'pgpt-runs/PG379/pg10169-cancel-six-compile-v2/snapshot'
OUT = data.BASE/'PG10186-protocol-module-preflight-v1'
PREFIX = 'src/schubert-nk-protocol/'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10169-cancel-six-compile-v2/manifest.json',
        '1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    prior_path = ROOT/'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9720-protocol-module-preflight-v1/cases.json'
    prior = data.read_checked(prior_path,'4b0cd8cf056bc6d7d86c7f7545fef0eceaaa17de3c1ce02aedb4ec513f4403a3')
    declared = []
    cases = []
    files = sorted(p for p in hashes if p.startswith(PREFIX+'src/test/java/') and p.endswith('.java'))
    assert len(files) == 23
    for path in files:
        text = (NORMAL/path).read_text()
        assert not any(mark in text for mark in ('@Disabled','@ParameterizedTest','@RepeatedTest','@TestFactory','@Nested',
            '@BeforeEach','@BeforeAll','@AfterEach','@AfterAll','@ExtendWith','@RegisterExtension','@TempDir',
            'System.getenv(', 'ProcessBuilder', 'java.lang.foreign', 'java.net.', 'java.sql.'))
        names = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        if not names:
            assert Path(path).name == 'IndependentNamedFieldOracle.java'
            continue
        qualified = path.removeprefix(PREFIX+'src/test/java/').removesuffix('.java').replace('/','.')
        target = NORMAL/PREFIX/'target/test-classes'/(qualified.replace('.','/')+'.class')
        raw = target.read_bytes()
        model = decode(raw,qualified.replace('.','/')+'.class')
        assert model['sourceFile'] == Path(path).name
        for name in names:
            assert len([m for m in model['methods'] if m['name'] == name and m['descriptor'] == '()V' and m['hasCode']]) == 1
            declared.append((qualified,name))
            cases.append(dict(className=qualified,method=name,path=path,sourceSha256=hashes[path],
                normalTestClassSha256=data.sha(raw),declarationOriginSource=SOURCE,
                declarationNamePriorSource='fd3d04df5710ca28f0e34f919cbc103e569a607b',oldDynamicResultTransferred=False))
    assert len(cases) == len(set(declared)) == 102 and len({r['path'] for r in cases}) == 22
    assert set(declared) == {(r['className'],r['method']) for r in prior}
    targets = NORMAL/PREFIX/'target/test-classes'
    physical = {str(p):data.sha(p.read_bytes()) for p in targets.rglob('*') if p.is_file()}
    resources = {}
    for path in sorted((ROOT/PREFIX/'src/test/resources').rglob('*')):
        if not path.is_file(): continue
        relative = str(path.relative_to(ROOT))
        target = targets/path.relative_to(ROOT/PREFIX/'src/test/resources')
        assert data.sha(path.read_bytes()) == data.sha(target.read_bytes()) == hashes[relative]
        resources[relative] = dict(sha256=hashes[relative],target=str(target))
    assert len(resources) == 5 and all(p.endswith('.tsv') for p in resources)
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    with zipfile.ZipFile(jar) as archive:
        main = {n:data.sha(archive.read(n)) for n in archive.namelist() if n.endswith('.class')}
    assert len(main) == 176 and all(n.startswith('dev/codex/schubert/nk/protocol/') for n in main)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=102,expectedSuites=22,
        normalManifestSha256='1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c',
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        physicalTestFiles=physical,fixtureFiles=resources,physicalMainClasses=main,allCurrentSourceInputHashes=hashes,
        declarationNamePriorSha256='4b0cd8cf056bc6d7d86c7f7545fef0eceaaa17de3c1ce02aedb4ec513f4403a3',
        compiledCurrentDescriptorChecked=True,oldSourceHashesNotClaimedEqual=True,declarationReuseNotProductPtTransfer=True,
        productTestsExecuted=0,newTestIds=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=len(cases),expectedSuites=len({r['className'] for r in cases}),
        mainClasses=len(main),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
