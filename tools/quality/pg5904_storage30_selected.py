"""All storage188 plus eleven dependency guards; ordinary self-owned fixtures only."""
import inspect
import pg5732_enum48_selected as engine
from pg5800_rollback_green import source_test_names

CASES = {**engine.CASES, 'storage': {
    'storage.' + p.stem for p in (engine.ROOT / 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage').glob('*Test.java')}}
COUNTS = {p.stem: len(source_test_names(p)) for p in
          (engine.ROOT / 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage').glob('*Test.java')}
COUNTS.update(PayloadGoldenVectorTest=3, EnumValueCatalogCompatibilityTest=1, HttpByteRangeParserTest=4)
TARGETS = {'storage': ['storage/' + n for n in (
    'LinuxExecDescriptors', 'LinuxFilesystemClassifier', 'LinuxSealedProof',
    'StorageAttributeGuard', 'StorageRootInspection', 'OwnedTransferDirectory')]}


def runner_source():
    if len(CASES['storage']) != 27 or sum(COUNTS[c.rsplit('.', 1)[1]] for c in CASES['storage']) != 188:
        raise ValueError('all existing storage188/27 without skips or aliases')
    raw = inspect.getsource(engine.main)
    changes = {
        "count=3 if module=='protocol'else 4 if module=='web'else 1": "count=COUNTS[cls.rsplit('.',1)[1]]",
        'sum(map(len,expected.values()))!=12 or len(expected)!=7': 'sum(map(len,expected.values()))!=199 or len(expected)!=33',
        "'expectedTests':12": "'expectedTests':199",
        "method=case.get('name','').removesuffix('()')": "method=case.get('name','').split('(',1)[0]",
        'len(physical)==1664': 'len(physical)==1666',
        'len(target_counters)==14': 'len(target_counters)==6',
        "with(out/'manifest.safe.json').open('x')as f:": "value.update(executionKind='NORMAL_STORAGE30_SELECTED199',noExternalRuntimeOperation=True,storageTests=188,fullSourceFormalQualificationPending=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact storage199 runner binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<all storage188 and eleven guards>', 'exec')
    return raw


def main():
    scope = {**vars(engine), 'SLOT': 'pg5904-storage30-selected199-v1', 'CASES': CASES,
             'COUNTS': COUNTS, 'TARGETS': TARGETS, 'test_names': source_test_names}
    exec(compile(runner_source(), '<storage199>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
