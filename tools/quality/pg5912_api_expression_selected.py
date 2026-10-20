"""Normal API24/temp dedicated DB and eleven guards; no live deployed environment."""
import inspect
import pg5732_enum48_selected as engine
from pg5800_rollback_green import source_test_names

CASES = {**engine.CASES, 'api': {
    'api.application.admin.UserCommandServiceTest', 'api.file.AssetChecksumManifestTest',
    'api.idempotency.SecretBufferTest', 'api.idempotency.ResponseSnapshotCodecTest'}}
COUNTS = dict(UserCommandServiceTest=10, AssetChecksumManifestTest=4, SecretBufferTest=3,
              ResponseSnapshotCodecTest=7, PayloadGoldenVectorTest=3,
              EnumValueCatalogCompatibilityTest=1, HttpByteRangeParserTest=4)
TARGETS = {'api': ['api/application/admin/UserCommandService', 'api/file/AssetChecksumManifest',
                   'api/idempotency/WipingByteArrayOutputStream']}


def runner_source():
    raw = inspect.getsource(engine.main)
    changes = {
        "count=3 if module=='protocol'else 4 if module=='web'else 1": "count=COUNTS[cls.rsplit('.',1)[1]]",
        'sum(map(len,expected.values()))!=12 or len(expected)!=7': 'sum(map(len,expected.values()))!=35 or len(expected)!=10',
        "'expectedTests':12": "'expectedTests':35",
        "method=case.get('name','').removesuffix('()')": "method=case.get('name','').split('(',1)[0]",
        'len(physical)==1664': 'len(physical)==1666',
        'len(target_counters)==14': 'len(target_counters)==3',
        "with(out/'manifest.safe.json').open('x')as f:": "value.update(executionKind='NORMAL_API_EXPRESSION_SELECTED35',noExternalRuntimeOperation=True,apiTests=24,fullSourceFormalQualificationPending=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact API35 runner binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<API35 independent fixture scope>', 'exec')
    return raw


def main():
    scope = {**vars(engine), 'SLOT': 'pg5912-api-expression-selected35-v1', 'CASES': CASES,
             'COUNTS': COUNTS, 'TARGETS': TARGETS, 'test_names': source_test_names}
    exec(compile(runner_source(), '<API35 fixture scope>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
