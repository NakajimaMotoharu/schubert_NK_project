"""Recover original before-text immutably; correct two generated names, never recapture modified sources."""
import copy
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from f03_literal_batch_sources import out,inverse
import pg13480_positioned_literal_config as old_cfg
import pg13481_positioned_literal_config_v2 as cfg
import f03_positioned_ascii_literals_v2 as fixed


def main():
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    old_manifest = data.read_checked(out(old_cfg,old_cfg.ORIGINAL_NUMBER)/'manifest.json','5bd16e69e95c23d19aacc2a5657f77a6383efe9df57946d1a60d9d93ce116d40')
    old = data.read_checked(out(old_cfg,old_cfg.ORIGINAL_NUMBER)/'originals.json',old_manifest['originalsSha256'])
    normal = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1])
    snapshot = data.ROOT.parent/'pgpt-runs/PG379/pg13468-residual-current-literal-v1/snapshot'
    assert normal['source'] == old['source'] == cfg.BASE_SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    failed = data.ROOT.parent/'pgpt-runs/PG379/pg13484-positioned-current-literal-v1'
    observed = data.read_checked(failed/'observed.safe.json','863ee07e07530211f79380b248d680f98c9e4da891686d03719e888ed905656e')
    assert observed['diagnosticComparisonMatched'] and observed['stages']['pmd']['actualExit'] == 4 and observed['stages']['checkstyle']['actualExit'] == 2
    ids,refs,_ = cfg.PREVIOUS_STATE()
    allowed = ids-refs
    value = copy.deepcopy(old)
    renamed = []
    for row in value['sources']:
        path = row['path']
        assert data.sha(row['text'].encode()) == row['sha256'] == normal['begin']['inputHashes'][path] == data.sha((snapshot/path).read_bytes())
        assert row['text'].encode() == (snapshot/path).read_bytes()
        assert data.sha((data.ROOT/path).read_bytes()) == observed['candidateSourceHashes'][path]
        inverse(row['text'],(data.ROOT/path).read_text(),row['mapping'])
        measured,binding = fixed.baseline(cfg,row)
        eligible = [r for r in row['findings'] if r['id'] in allowed]
        updated = fixed.select(row['text'],row['sha256'],eligible,measured,allowed,len(row['mapping']))
        expected = copy.deepcopy(row['mapping'])
        for item in expected:
            name = fixed.constant_name(item['value'],item['literal'])
            if name != item['name']:
                renamed.append(dict(path=path,oldName=item['name'],newName=name,references=item['references']))
            item['name'] = name
        assert updated == expected and row['currentDiagnosticBaseline'] == binding
        row['mapping'] = updated
        row['selectionMetadataVectors'] = fixed.metadata_vectors(row['text'],row['sha256'],eligible,measured,allowed,updated)
    assert len(renamed) == 2 and len(value['sources']) == 22 and sum(len(r['mapping']) for r in value['sources']) == 91
    invalid = {}
    for path,sha in normal['begin']['inputHashes'].items():
        current = (data.ROOT/path).read_bytes()
        if path not in cfg.PATHS:
            assert data.sha(current) == sha
        if path.endswith('.java'):
            names = {token for token in fixed.tokens(current.decode()) if token.startswith('FIXTURE_')}
            bad = sorted(name for name in names if not re.fullmatch(r'[A-Z][A-Z0-9]*(_[A-Z0-9]+)*',name))
            if bad:
                invalid[path] = bad
    assert invalid == {row['path']:[row['oldName']] for row in renamed}
    vectors = fixed.name_vectors()
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',value)
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,originalsSha256=data.sha((target/'originals.json').read_bytes()),
        originalBeforeTextManifestSha256='5bd16e69e95c23d19aacc2a5657f77a6383efe9df57946d1a60d9d93ce116d40',normalManifestSha256=cfg.OLD_NORMAL[1],originalBeforeTextRecaptured=False,
        sourcePaths=list(cfg.PATHS),selectedLiteralDiagnostics=91,selectionMetadataNegativeVectors=sum(r['selectionMetadataVectors']['negative'] for r in value['sources']),
        currentDiagnosticBaselines={r['path']:r['currentDiagnosticBaseline'] for r in value['sources']},renamedConstants=renamed,nameBoundaryVectors=vectors,
        allCurrentJavaFixtureIdentifierScan=dict(invalidNamesBeforeRepair=invalid,scope='ALL_NORMAL_INPUT_JAVA_SOURCES_ONLY_NO_HELD_TOOLS'),
        originalFailedPreflight=dict(actualExit=1,observedSha256='863ee07e07530211f79380b248d680f98c9e4da891686d03719e888ed905656e',pmdExit=4,checkstyleExit=2),
        sourceModified=False,productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
