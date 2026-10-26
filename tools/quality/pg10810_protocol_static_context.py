"""Exactly ten unchanged-intent PMD contexts with vendor/source/current-run binding; raw retained."""
from collections import Counter
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10810-protocol-static-context-v1'
SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
EXPECTED = Counter(UseConcurrentHashMap=5,CompareObjectsWithEquals=2,DoNotUseThreads=2,NullAssignment=1)


def attributes(value):
    return {k:v for k,v in value.items() if k not in ('beginline','endline','begincolumn','endcolumn')}


def validate(rows,hashes,ids):
    if len(rows) != 10 or {r['originalFindingId'] for r in rows} != ids or len(ids) != 10:
        raise ValueError('each exact original finding once')
    if Counter(r['rule'] for r in rows) != EXPECTED:
        raise ValueError('only fixed ten concrete rule contexts')
    if any(r['sourceSha256'] != hashes.get(r['path']) or r['disposition'] != 'NOT_APPLICABLE_EXACT_SOURCE_CONTEXT' or r['source'] != SOURCE for r in rows):
        raise ValueError('exact source and explicit non-executed review status')
    if any(r['scopeGeneralized'] or r['rawSuppressed'] or r['newProductExecutions'] for r in rows):
        raise ValueError('no blanket exemption, raw suppression or invented PT')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    raw_path = data.BASE/'PG10806-protocol-quality-module-static-v1/manifest.json'
    raw = data.read_checked(raw_path,'21e4e7d595f27d5404a7bf2c97405bd18f41cce0a7ad934de29eb3983ab2368f')
    proof = data.read_checked(data.BASE/'PG10808-protocol-quality-post-v1/manifest.json',
        'd19e6b96aab7c1487bef2757d1f2b5b312d41fc2a6995d977c2ff0c0a8b0fda5')
    assert raw['source'] == proof['source'] == SOURCE and raw['actualExit'] == 1 and proof['actualExit'] == 0
    assert proof['protocolFourCounters100'] and proof['testExecutions'] == 102
    assert raw['reports']['pmd']['findings'] == 10 and raw['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in raw['reports'].values())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in raw['sourceHashes'].items())
    xml_path = raw_path.parent/'pmd.xml'
    assert data.sha(xml_path.read_bytes()) == raw['reports']['pmd']['sha256']
    old_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    assert data.sha(old_path.read_bytes()) == '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
    original = json.loads(old_path.read_bytes())
    vendor = data.ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert data.sha(vendor.read_bytes()) == '068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    definitions = {}
    ns = {'x':'http://pmd.sourceforge.net/ruleset/2.0.0'}
    with zipfile.ZipFile(vendor) as jar:
        for name in ('category/java/multithreading.xml','category/java/errorprone.xml'):
            for node in ET.fromstring(jar.read(name)):
                if node.get('name') in EXPECTED:
                    definitions[node.get('name')] = dict(resource=name,description=''.join(node.find('x:description',ns).itertext()).strip())
    assert set(definitions) == set(EXPECTED) and 'J2EE' in definitions['DoNotUseThreads']['description']
    assert 'multi-threaded' in definitions['UseConcurrentHashMap']['description']
    prepared = data.read_checked(data.BASE/'PG10802-protocol-quality-preflight-v1/manifest.json',
        '8d0eaed1b32f344822bf7cdba354e8272de1d4340fbd2fc6bca8f942cb17cd58')
    cases = data.read_checked(data.BASE/'PG10802-protocol-quality-preflight-v1/cases.json',prepared['casesSha256'])
    prefix = 'src/schubert-nk-protocol/src/'
    oracle_path = prefix+'test/java/dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle.java'
    oracle = (data.ROOT/oracle_path).read_text()
    assert not any(word in oracle for word in ('Executors','Thread','CompletableFuture','.parallel','setAccessible'))
    copied_path = prefix+'main/java/dev/codex/schubert/nk/protocol/layout/FieldValueSet.java'
    copied = (data.ROOT/copied_path).read_text()
    assert 'LinkedHashMap<String, FieldValue> copy = new LinkedHashMap<>();' in copied and 'Collections.unmodifiableMap(copy)' in copied
    rows = []
    for file in ET.fromstring(xml_path.read_bytes()):
        if file.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        text = (data.ROOT/path).read_text()
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation': continue
            rule = node.get('rule')
            assert rule in EXPECTED
            matches = [r for r in original if r['path'] == path and r['rule'] == rule
                and attributes(r['attributes']) == attributes(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            if rule == 'UseConcurrentHashMap':
                variable = node.get('variable')
                if Path(path).name == 'PayloadCodec.java':
                    assert variable == 'values' and node.get('method') == 'decodeArea'
                    method = text.split('private static FieldValueSet decodeArea(',1)[1].split('private static void validateNames(',1)[0]
                    assert 'Map<String, FieldValue> values = new LinkedHashMap<>();' in method and 'return new FieldValueSet(values);' in method
                    related = 'PayloadGoldenVectorTest'
                else:
                    assert path == oracle_path and variable in ('accessors','areas','reviewed','absent')
                    assert node.get('method') == ('verifyType' if variable == 'absent' else 'verifyAll')
                    assert 'Map<String, FieldValue> absent = new LinkedHashMap<>(input);' in oracle
                    related = 'PayloadTypeCatalogTest'
                reason = 'METHOD_LOCAL_EXCLUSIVE_MAP_NO_CONCURRENT_ACCESS; immutable FieldValueSet copy at boundary'
            elif rule == 'CompareObjectsWithEquals':
                if Path(path).name == 'FailedJmsIsolationException.java':
                    assert 'if (protocolFailure != primary)' in text and 'addSuppressed(protocolFailure)' in text
                    related = 'FailedJmsIsolationExceptionTest'
                else:
                    assert Path(path).name == 'UnconfirmedJmsRollbackException.java'
                    assert 'if (rollbackFailure != primary)' in text and 'addSuppressed(rollbackFailure)' in text
                    related = 'UnconfirmedJmsRollbackExceptionTest'
                reason = 'APPROVED_THROWABLE_NODE_IDENTITY_NOT_VALUE_EQUALITY; SS321/322 PG-D441/442'
            elif rule == 'DoNotUseThreads':
                assert Path(path).name == 'PayloadGoldenVectorTest.java' and node.get('method') == 'sharedCodecProducesIdenticalBytesUnderConcurrentUse'
                assert 'try (var executor = Executors.newFixedThreadPool(8))' in text and 'new CountDownLatch(8)' in text
                assert prepared['judgement'] == 'PT_DEFAULT_CONCRETE_PROTOCOL_ONLY_MODULE_REGRESSION'
                reason = 'J2EE_RULE_PRECONDITION_FALSE_FOR_STANDALONE_PROTOCOL_ONLY_JUNIT; own finite executor/TWR retained'
                related = 'PayloadGoldenVectorTest'
            else:
                assert path == oracle_path and node.get('method') == 'verifyType'
                assert 'Object[] bad = arguments.toArray();' in oracle and 'bad[n] = null;' in oracle
                assert 'constructor.newInstance(bad)' in oracle and 'assertInstanceOf(NullPointerException.class' in oracle
                reason = 'REQUIRED_NULL_CONSTRUCTOR_NEGATIVE_INPUT_NOT_PRODUCTION_NULL_FLOW'
                related = 'PayloadTypeCatalogTest'
            tests = [r['testId'] for r in cases if r['className'].endswith('.'+related)]
            assert tests
            rows.append(dict(originalFindingId=old['id'],source=SOURCE,path=path,sourceSha256=raw['sourceHashes'][path],
                rule=rule,actualAttributes=node.attrib,actualMessage=(node.text or '').strip(),originalMessage=old['message'],originalRowSha256=old['rowSha256'],reason=reason,
                disposition='NOT_APPLICABLE_EXACT_SOURCE_CONTEXT',relatedTestIds=tests,reviewIsNewTestExecution=False,
                scopeGeneralized=False,rawSuppressed=False,newProductExecutions=0))
    ids = {r['originalFindingId'] for r in rows}
    validate(rows,raw['sourceHashes'],ids)
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','wrong-source'),('scopeGeneralized',True),('rawSuppressed',True)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: validate(bad,raw['sourceHashes'],ids)
        except ValueError: pass
        else: raise AssertionError('incomplete/stale/blanket disposition accepted')
    decision = data.ROOT/'documents/400_PGPT/440_判断/441_実装判断記録.md'
    assert '## PG-D682' in decision.read_text()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'vendor-rule-descriptions.json',definitions)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        rawManifestSha256=data.sha(raw_path.read_bytes()),rawStaticExit=1,rawPmd=10,concreteNotApplicable=10,
        unclassified=0,applicableUnresolved=0,ruleCounts=dict(EXPECTED),sourceHashes=raw['sourceHashes'],
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),vendorJarSha256=data.sha(vendor.read_bytes()),
        vendorDescriptionSha256=data.sha((OUT/'vendor-rule-descriptions.json').read_bytes()),judgement='PG-D682',
        judgementDocumentSha256=data.sha(decision.read_bytes()),currentRuntimeProof='PG10808',metadataNegativeVectors=len(bads),
        suppressionsAdded=False,scopeGeneralized=False,productTestsExecuted=0,externalActions=0,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
