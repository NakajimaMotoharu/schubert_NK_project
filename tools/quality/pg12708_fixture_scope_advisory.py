"""Metadata-only original-owner/import advisory and independent fixed dictionary vectors."""
import copy
import hashlib
import json
import g07_host_class_provenance_inputs as data
from fixture_scope_advisory import audit, direct_imports, java_path
from host_tool_invocation import capture, verify
import pg12684_scenario_writer_plan as plan

SOURCE = 'e353b1f49a740a426031fdc199f7ce8b26081971'
OUT = data.BASE/'PG12708-fixture-scope-advisory-v1'
NORMAL = ('PG12686-scenario-writer-six-compile-v1', '20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d')
REGISTRY = ('PG12700-scenario-writer-trace-v2', '1a578401cdce20798948deeb8b30322a0d0a663a79ea5ce2b6a04abc983e877f')
EXTRA = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/scenario/ScenarioEntryRecord.java'


def selftest():
    prefix = 'src/schubert-nk-protocol/src/'
    a = prefix+'main/java/dev/codex/schubert/nk/protocol/A.java'
    b = prefix+'main/java/dev/codex/schubert/nk/protocol/B.java'
    t = prefix+'test/java/dev/codex/schubert/nk/protocol/ATest.java'
    texts = {a: 'class A {}', b: 'class B {}', t: 'import dev.codex.schubert.nk.protocol.A; import static dev.codex.schubert.nk.protocol.B.Inner.VALUE; class ATest {}'}
    hashes = {p: hashlib.sha256(v.encode()).hexdigest() for p, v in texts.items()}
    rows = [dict(path=t, sha256=hashes[t], canonicalOwner='WBS-P008-06', canonicalCostOwner='WBS-P008-03')]
    args = dict(texts=texts, reviewed_main=[a,b], changed_paths=[t], frozen_hashes=hashes, registry_rows=rows, known_wbs={'WBS-P008-06','WBS-P008-03'})
    result = audit(**args)
    assert result['metadataConsistent'] and result['originalOwners'] == [dict(path=t, canonicalOwner='WBS-P008-06', canonicalCostOwner='WBS-P008-03')]
    assert result['directImports'][t] == [dict(name='dev.codex.schubert.nk.protocol.A', static=False, outerSourceCandidate=a), dict(name='dev.codex.schubert.nk.protocol.B.Inner.VALUE', static=True, outerSourceCandidate=b)]
    assert result['executionQualified'] is False and result['holdReleased'] is False
    quoted = '// import dev.codex.schubert.nk.X;\n/* import dev.codex.schubert.nk.Y; */\nString s="import dev.codex.schubert.nk.Z;"; String v="""import dev.codex.schubert.nk.Q;""";'
    assert direct_imports(quoted) == []
    labels = []
    cases = []
    def variant(label, **changes):
        changed = copy.deepcopy(args)
        changed.update(changes)
        assert changed != args
        cases.append((label, changed))
    variant('missing-reviewed', reviewed_main=[a])
    variant('missing-row', registry_rows=[])
    variant('wrong-owner-expectation', expected_owners={t: ('WBS-P008-03','WBS-P008-03')})
    variant('unknown-owner', known_wbs={'WBS-P008-06'})
    variant('row-source-mismatch', registry_rows=[dict(rows[0],sha256='0'*64)])
    variant('duplicate-row', registry_rows=rows+rows)
    variant('duplicate-reviewed', reviewed_main=[a,b,b])
    variant('duplicate-changed', changed_paths=[t,t])
    variant('missing-text', texts={a:texts[a], t:texts[t]})
    variant('changed-byte', texts={**texts, t:texts[t]+' '})
    variant('frozen-invalid-hash', frozen_hashes={**hashes,t:'not-sha'})
    variant('test-as-main', reviewed_main=[a,b,t])
    variant('owner-expectation-outside-scope', expected_owners={a:('WBS-P008-06','WBS-P008-03')})
    variant('ambiguous-definition', frozen_hashes={**hashes,a.replace('schubert-nk-protocol','schubert-nk-api'):'1'*64})
    for label, candidate in cases:
        try:
            observed = audit(**candidate)
        except ValueError:
            labels.append(label)
        else:
            assert not observed['metadataConsistent'] and observed['metadataIssues']
            labels.append(label)
    for label, text in [('wildcard','import dev.codex.schubert.nk.protocol.*;'), ('unresolved','import dev.codex.schubert.nk.protocol.Missing;'), ('unicode',r'class ATest { String x="\u0041"; }')]:
        candidate = copy.deepcopy(args)
        candidate['texts'][t] = text
        candidate['frozen_hashes'][t] = hashlib.sha256(text.encode()).hexdigest()
        candidate['registry_rows'][0]['sha256'] = candidate['frozen_hashes'][t]
        assert candidate != args and not audit(**candidate)['metadataConsistent']
        labels.append(label)
    for bad in ['../x.java', '/tmp/X.java', a.replace('/main/', '/main/../main/'), 'tools/quality/architecture/SnapshotKeyCloseWitness.java', 'tools/quality/pg9892_snapshot_key_close_witness.py']:
        try:
            java_path(bad)
        except ValueError:
            labels.append('path-rejected:'+bad)
        else:
            raise AssertionError('noncanonical path accepted')
    for bad in ['import dev.codex.schubert.nk.protocol.A', 'import dev.codex.schubert.nk.protocol.A();']:
        try:
            direct_imports(bad)
        except ValueError:
            labels.append('malformed-import:'+bad)
        else:
            raise AssertionError('malformed import accepted')
    return dict(positiveVectors=3, negativeVectors=len(labels), nonVacuousNegativeLabels=labels)


def inputs():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json', NORMAL[1])
    registry = data.read_checked(data.BASE/REGISTRY[0]/'manifest.json', REGISTRY[1])
    assert normal['source'] == registry['source'] == SOURCE and normal['actualExit'] == registry['actualExit'] == 0
    reviewed = [*plan.eligibility(), EXTRA]
    paths = [*reviewed, plan.PATH, plan.COMPANION]
    assert len(reviewed) == 57 and len(paths) == len(set(paths)) == 59
    # Explicit reviewed paths only: never enumerate filesystem or inspect held tools.
    texts = {p:(data.ROOT/p).read_text() for p in paths}
    nodes = {}
    def collect(item):
        if isinstance(item, dict):
            if isinstance(item.get('id'), str):
                nodes[item['id']] = item
            for child in item.values():
                collect(child)
        elif isinstance(item, list):
            for child in item:
                collect(child)
    for name in ['481_PGPT詳細WBS.json', '484_WBSコスト枠・細分化.json']:
        collect(json.loads((data.ROOT/'documents/400_PGPT/470_PMO'/name).read_bytes()))
    leaves = {key for key, value in nodes.items() if not value.get('children')}
    return dict(texts=texts,reviewed_main=reviewed,changed_paths=[plan.PATH,plan.COMPANION],frozen_hashes=normal['begin']['inputHashes'],registry_rows=registry['sourceRows'],known_wbs=leaves)


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    vectors = selftest()
    args = inputs()
    result = audit(**args)
    assert result['metadataConsistent']
    missing = audit(**{**args,'reviewed_main':[p for p in args['reviewed_main'] if p != EXTRA]})
    assert any(r['kind']=='DIRECT_IMPORT_NOT_REVIEWED' and r['target']==EXTRA for r in missing['metadataIssues'])
    wrong = audit(**{**args,'expected_owners':{plan.PATH:('WBS-P008-03','WBS-P008-03')}})
    assert any(r['kind']=='EXPECTED_OWNER_DIFFERS_FROM_ORIGINAL' and r['path']==plan.PATH for r in wrong['metadataIssues'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL[1],registryManifestSha256=REGISTRY[1],reviewedMainCount=57,explicitTextCount=59,inputHashes={p:args['frozen_hashes'][p] for p in args['texts']},selftest=vectors,reproducedPriorMetadataDefects=['BUG1993','BUG1994'],priorDefectAdvisoryIssues=missing['metadataIssues']+wrong['metadataIssues'],**result))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
