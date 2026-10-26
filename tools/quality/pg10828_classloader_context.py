"""542 fixed current ClassLoader contexts, reuse exact architecture but inspect this vendor premise separately."""
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10828-classloader-context-v1'


def validate(rows,reference,hashes,roles):
    if len(rows) != 542 or Counter(r['id'] for r in rows) != Counter(reference.keys()):
        raise ValueError('exact original542 findings')
    for row in rows:
        old = reference[row['id']]
        if row['path'] != old['path'] or row['coordinates'] != old['attributes'] or row['rule'] != 'UseProperClassLoader':
            raise ValueError('exact single rule/path/original coordinates')
        if row['source'] != SOURCE or row['sourceSha256'] != hashes.get(row['path']) or row['sourceSha256'] != old['inputSha256']:
            raise ValueError('exact current unchanged input')
        if row['approvedRole'] != roles[old['module']]['approvedRole'] or row['disposition'] != 'CONTEXT_NOT_APPLICABLE_J2EE_CLASSLOADER_PREMISE':
            raise ValueError('approved own module role and exact context')
        if row['qualityGatePass'] or row['productTestsExecuted'] or row['foreignContainerSupportProven'] or not row['dynamicAuthorizationUnchanged']:
            raise ValueError('no inferred runtime support/PT/authorization/PASS')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    architecture_path = data.BASE/'PG10822-global-thread-context-v1/architecture.json'
    architecture = data.read_checked(architecture_path,'3ebea6b5e82692a68fe91af9552d8dc2206d67395c573ff46028d658cc4b612c')
    assert architecture['source'] == SOURCE and not architecture['actualVmOrServiceConfigurationObserved']
    hashes = architecture['allCurrentInputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    original = data.read_checked(raw_path,'92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['rule'] == 'UseProperClassLoader']
    assert len(selected) == 542 and Counter(r['sourceKind'] for r in selected) == Counter(MAIN=1,TEST=541)
    assert len({r['path'] for r in selected}) == 206
    vendor = data.ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert data.sha(vendor.read_bytes()) == architecture['vendorJarSha256']
    with zipfile.ZipFile(vendor) as jar:
        raw_rule = jar.read('category/java/errorprone.xml')
    node = next(r for r in ET.fromstring(raw_rule) if r.get('name') == 'UseProperClassLoader')
    description = ''.join(node.find('{http://pmd.sourceforge.net/ruleset/2.0.0}description').itertext()).strip()
    assert 'In J2EE' in description and 'getClassLoader()' in description and 'getContextClassLoader()' in description
    prior_path = data.BASE/'PG5760-changed-context-v1/manifest.json'
    prior = data.read_checked(prior_path,'12669fc9fb3f225310894b08c430f38c07dd6ffd9f76a029c0a752cd967f6737')
    assert prior['actualExit'] == 0 and not prior['F03Accepted'] and not prior['sourceCodeChanged']
    rows = []
    for old in selected:
        path = old['path']
        raw = (data.ROOT/path).read_bytes()
        assert data.sha(raw) == old['inputSha256'] == hashes[path]
        lines = raw.decode().splitlines(keepends=True)
        low,high = int(old['attributes']['beginline']),int(old['attributes']['endline'])
        assert 1 <= low <= high <= len(lines)
        span = ''.join(lines[low-1:high])
        assert 'getClassLoader(' in span
        module = old['module']
        assert module in architecture['moduleRoles']
        if old['sourceKind'] == 'MAIN':
            assert old['id'] == 'PMD-07210' and Path(path).name == 'WebHttpServer.java'
            assert 'context.setParentClassLoader(WebHttpServer.class.getClassLoader());' in span
            basis = 'CURRENT_OWN_RELEASE_EMBEDDED_PARENT_LOADER; old PG5760 premise reference only, current input reauthenticated'
        else:
            assert '/src/test/java/' in path
            basis = 'CURRENT_JUNIT_FIXTURE_IN_APPROVED_STANDALONE_GRAPH; no foreign managed J2EE container premise'
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=hashes[path],rule=old['rule'],
            sourceKind=old['sourceKind'],coordinates=old['attributes'],originalRowSha256=old['rowSha256'],lineSpanSha256=data.sha(span.encode()),
            approvedRole=architecture['moduleRoles'][module]['approvedRole'],basis=basis,
            disposition='CONTEXT_NOT_APPLICABLE_J2EE_CLASSLOADER_PREMISE',qualityGatePass=False,
            productTestsExecuted=0,dynamicAuthorizationUnchanged=True,foreignContainerSupportProven=False))
    validate(rows,{r['id']:r for r in selected},hashes,architecture['moduleRoles'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'dispositions.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        architectureManifestSha256=data.sha(architecture_path.read_bytes()),originalIndexSha256=data.sha(raw_path.read_bytes()),
        vendorJarSha256=data.sha(vendor.read_bytes()),vendorRuleResourceSha256=data.sha(raw_rule),vendorDescription=description,
        sourceFiles=206,rawClassLoaderFindings=542,main=1,test=541,dispositionsSha256=data.sha((OUT/'dispositions.json').read_bytes()),
        historicalMainPremiseManifestSha256=data.sha(prior_path.read_bytes()),judgement='PG-D684',
        rawWarningsRemoved=0,sourceChanged=False,suppressionsAdded=False,productTestsExecuted=0,
        newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,dynamicAuthorizationUnchanged=True,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
