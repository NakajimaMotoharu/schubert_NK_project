"""BUG1726 append-only2069 correction and five-group source check; no product rerun/cost change."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from host_tool_invocation import capture, verify
from public_blob_scan import sha
from source_evidence_binding import bind
import pg998_metrics as metrics

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT = BASE / 'PG8974-metric-source-correction-v1'
SOURCE = 'fb9fce0f91de3d9fdfa634fe277592700f915e45'
PROOFS = [
 ('2058','PG8858-api-caller-metric-post-v1','05b78b6b1236e1383aa4ae6bc5a9212cb818eb4c73f959f531446133a9a2dc23'),
 ('2060','PG8872-web-caller-metric-post-v1','177a2494065726f470a17053fed0cc47e6d06ae1d897bc3ea1f9a1d285b37aa0'),
 ('2064','PG8914-batch-full-text-static-fixed-post-v1','68b7069b5534b06276978c01838c0c91ca53aab48c90424f9ccaa13b444ee289'),
 ('2066','PG8936-web-service-metric-fixed-post-v1','4e3d2c24ec8c54988f5d45cdc09402eb0729c6477a754ebd77482efd7ff520c7'),
 ('2069','PG8950-web-metric-pipeline-post-v1','46b55585fd64cb659bfc0066327219c5b690bd9f7b47f07e8d931e9dd025fb3b')]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    events = [json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    by_id = {row['eventId']: row for row in events}
    assert not any(row.get('correctsEventId') == 'PGPT-20261008-2069' for row in events)
    observations = []
    for suffix, directory, digest in PROOFS:
        path = BASE / directory / 'manifest.json'
        data = path.read_bytes(); assert sha(data) == digest
        actual = json.loads(data)['source']
        proof = bind([(path, digest)], actual)
        event = by_id['PGPT-20261008-' + suffix]
        observations.append(dict(eventId=event['eventId'], reportedSource=event['source'],
                                 actualSource=actual, consistent=event['source'] == actual, proofs=proof))
    assert [row['eventId'] for row in observations if not row['consistent']] == ['PGPT-20261008-2069']
    trace = BASE / 'PG8952-web-metric-pipeline-trace-v1/manifest.json'
    joined = bind([(BASE / PROOFS[-1][1] / 'manifest.json', PROOFS[-1][2]),
                   (trace, '85aac967c065ccad21eb917a0787fa96fc5bcd8c581bb254738aadccc087e4a0')], SOURCE)
    rejected = []
    with TemporaryDirectory(prefix='pg8974-source-guard-', dir=ROOT.parent / 'pgpt-runs/PG379') as temporary:
        path = Path(temporary) / 'synthetic.safe.json'
        golden = dict(actualExit=0, source='1' * 40)
        path.write_text(json.dumps(golden))
        digest = sha(path.read_bytes())
        assert bind([(path, digest)], '1' * 40)[0]['source'] == '1' * 40
        cases = [('wrong-source', golden, '2' * 40, None),
                 ('failed-exit', dict(actualExit=1, source='1'*40), '1'*40, None),
                 ('bool-exit', dict(actualExit=False, source='1'*40), '1'*40, None),
                 ('missing-source', dict(actualExit=0), '1'*40, None),
                 ('wrong-hash', golden, '1'*40, '0'*64)]
        for name, body, source, forced_hash in cases:
            path.write_text(json.dumps(copy.deepcopy(body)))
            try:
                bind([(path, forced_hash or sha(path.read_bytes()))], source)
            except ValueError:
                rejected.append(name)
            else:
                raise AssertionError('source binding rejected no mismatch')
    verify(invocation)
    original = by_id['PGPT-20261008-2069']
    correction = metrics.append(original['groupId'], 'CHECKPOINT', dict(
         primaryWbs='WBS-P018-09', source=SOURCE, workCategory='ADMIN',
         correctsEventId=original['eventId'], correctionKind='APPEND_ONLY_SOURCE_ASSOCIATION_NOT_NEW_COMPLETION',
         originalEventCanonicalSha256=sha(json.dumps(original,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),
         correctedFields={'source': {'previous': original['source'], 'value': SOURCE}},
         sourceProofs=joined, sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1843_計測source追記訂正・横展開結果.md'],
         technicalMeasurementDelta={'newTestIds':0,'newMain':0,'newAccepted':0},
         originalTechnicalMeasurementDeltaUnchanged=True, costReallocated=False, regressionExecuted=False,
         failureIds=['BUG-1726','YKT-1477'], attemptResult='SOURCE_ONLY_CORRECTION; ORIGINAL_EVENT_AND_MEASUREMENTS_PRESERVED',
         nextCommand='Continue current G07 scan evidence recording; no product/test rerun', pgptAllComplete=False))
    after = [json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert next(row for row in after if row['eventId'] == original['eventId']) == original
    assert len([row for row in after if row.get('correctsEventId') == original['eventId']]) == 1
    OUT.mkdir()
    value = dict(actualExit=0,invocation=invocation,source=SOURCE,bug='BUG-1726',ykt='YKT-1477',
          originalEventId=original['eventId'],correctionEventId=correction,originalPreserved=True,
          sourceBindings=joined,relatedGroups=observations,rejectedMetadataCases=rejected,
          productTestsExecuted=0,newAccepted=0,costReallocated=False,formalUpdated=False)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,correctionEventId=correction,groupsChecked=5,mismatches=1,negativeCases=len(rejected))))


if __name__ == '__main__':
    main()
