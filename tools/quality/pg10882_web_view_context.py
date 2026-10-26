"""Exact17 remaining Web view PMD source contexts, original raw retained; no product execution."""
from collections import Counter
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '787dc7da7c9643789326f7a4002931e9b7497f04'
OUT = data.BASE/'PG10882-web-view-context-v1'
EXPECTED = Counter(DoNotUseThreads=16,UseConcurrentHashMap=1)


def attributes(value):
    return {k:v for k,v in value.items() if k not in ('beginline','endline','begincolumn','endcolumn')}


def validate(rows,hashes,ids):
    if len(rows) != 17 or Counter(r['rule'] for r in rows) != EXPECTED:
        raise ValueError('exact17 concrete rows')
    if len(ids) != 17 or {r['originalFindingId'] for r in rows} != ids:
        raise ValueError('each original id exactly once')
    if any(r['source'] != SOURCE or r['sourceSha256'] != hashes.get(r['path']) or r['disposition'] != 'NOT_APPLICABLE_EXACT_SOURCE_CONTEXT' for r in rows):
        raise ValueError('exact source/hash context')
    if any(r['scopeGeneralized'] or r['rawSuppressed'] or r['newProductExecutions'] for r in rows):
        raise ValueError('no global exemption/suppression/invented PT')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    raw_path = data.BASE/'PG10880-web-boundary-complete-static-v1/manifest.json'
    raw = json.loads(raw_path.read_bytes())
    assert raw['actualExit'] == 1 and raw['source'] == SOURCE
    assert raw['reports']['pmd']['findings'] == 17 and raw['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in raw['reports'].values())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in raw['sourceHashes'].items())
    xml_path = raw_path.parent/'pmd.xml'
    assert data.sha(xml_path.read_bytes()) == raw['reports']['pmd']['sha256']
    original_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    assert data.sha(original_path.read_bytes()) == '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
    original = json.loads(original_path.read_bytes())
    architecture_path = data.BASE/'PG10822-global-thread-context-v1/architecture.json'
    assert data.sha(architecture_path.read_bytes()) == '3ebea6b5e82692a68fe91af9552d8dc2206d67395c573ff46028d658cc4b612c'
    architecture = json.loads(architecture_path.read_bytes())
    assert architecture['actualVmOrServiceConfigurationObserved'] is False
    premises = {p:h for p,h in architecture['allCurrentInputHashes'].items() if '/src/main/' in p or p.endswith('pom.xml')}
    assert premises and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in premises.items())
    vendor = data.ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert data.sha(vendor.read_bytes()) == '068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    definitions = {}
    ns = {'x':'http://pmd.sourceforge.net/ruleset/2.0.0'}
    with zipfile.ZipFile(vendor) as jar:
        for resource in ('category/java/multithreading.xml','category/java/errorprone.xml'):
            for node in ET.fromstring(jar.read(resource)):
                if node.get('name') in EXPECTED:
                    definitions[node.get('name')] = dict(resource=resource,description=''.join(node.find('x:description',ns).itertext()).strip())
    assert set(definitions) == set(EXPECTED)
    assert 'J2EE' in definitions['DoNotUseThreads']['description'] and 'multi-threaded' in definitions['UseConcurrentHashMap']['description']
    rows = []
    for file in ET.fromstring(xml_path.read_bytes()):
        if file.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        text = (data.ROOT/path).read_text()
        assert path in raw['sourceHashes']
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation': continue
            rule = node.get('rule')
            matches = [r for r in original if r['path'] == path and r['rule'] == rule and
                attributes(r['attributes']) == attributes(node.attrib) and
                ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            if rule == 'DoNotUseThreads':
                assert 'Executors.newFixedThreadPool(8)' in text and 'TimeUnit.SECONDS' in text and '64' in text
                assert 'try (' in text and node.get('method') in text and ('Concurrent' in node.get('method'))
                reason = 'STANDALONE_JUNIT_NOT_J2EE; exact own8worker/64task with Future10or20s and TWR; not runtime ownership proof'
            else:
                assert rule == 'UseConcurrentHashMap' and Path(path).name == 'ScenarioDetailTemplateTest.java'
                assert node.get('method') == 'detail023CssAndViewBoundary' and node.get('variable') == 'declarations'
                body = text.split('void detail023CssAndViewBoundary()',1)[1].split('void detail024ConcurrentRendering()',1)[0]
                assert 'Map<String, String> declarations = new LinkedHashMap<>();' in body
                assert not any(word in body for word in ('pool','submit(','Thread','Executors','.parallel'))
                assert body.count('declarations.put(') >= 10 and 'declarations.clear();' in body
                reason = 'EXCLUSIVE_METHOD_LOCAL_SEQUENTIAL_CSS_EXPECTED_ORDER_MAP; never passed to concurrent detail024'
            rows.append(dict(originalFindingId=old['id'],source=SOURCE,path=path,sourceSha256=raw['sourceHashes'][path],
                rule=rule,actualAttributes=node.attrib,actualMessage=(node.text or '').strip(),originalRowSha256=old['rowSha256'],
                reason=reason,disposition='NOT_APPLICABLE_EXACT_SOURCE_CONTEXT',scopeGeneralized=False,rawSuppressed=False,newProductExecutions=0))
    ids = {r['originalFindingId'] for r in rows}
    validate(rows,raw['sourceHashes'],ids)
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','wrong'),('scopeGeneralized',True),('rawSuppressed',True),('newProductExecutions',1)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: validate(bad,raw['sourceHashes'],ids)
        except ValueError: pass
        else: raise AssertionError('stale/partial/blanket context accepted')
    decision = data.ROOT/'documents/400_PGPT/440_判断/441_実装判断記録.md'
    assert '## PG-D685' in decision.read_text()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'vendor-rule-descriptions.json',definitions)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        rawManifestSha256=data.sha(raw_path.read_bytes()),rawStaticExit=1,rawPmd=17,concreteNotApplicable=17,
        unclassified=0,applicableUnresolved=0,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        sourceHashes=raw['sourceHashes'],vendorJarSha256=data.sha(vendor.read_bytes()),
        vendorDescriptionSha256=data.sha((OUT/'vendor-rule-descriptions.json').read_bytes()),
        architectureSha256=data.sha(architecture_path.read_bytes()),currentMainAndPomPremises=premises,ruleCounts=dict(EXPECTED),
        judgement='PG-D685',judgementDocumentSha256=data.sha(decision.read_bytes()),metadataNegativeVectors=len(bads),
        prior68RuntimeSource='d959404cdef9bdfaa9be8de5a3c787db13a72c1a',priorRuntimeReassigned=False,
        sourceInputReviewIsDynamicTestSuccess=False,scopeGeneralized=False,suppressionsAdded=False,
        productTestsExecuted=0,coverage=None,externalActions=0,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
