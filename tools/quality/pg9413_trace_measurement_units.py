"""Append immutable-evidence unit corrections only; no target tool/test replay or cost change."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9413-trace-measurement-units-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def counts(mapping):
    if not mapping or any(not isinstance(row.get('path'),str) for row in mapping.values()):raise ValueError('nonempty class-to-source path map required')
    return dict(mainClassDeclarations=len(mapping),uniqueMainSourceFiles=len({row['path'] for row in mapping.values()}))

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert counts({'a':dict(path='p/A.java'),'b':dict(path='p/A.java')})==dict(mainClassDeclarations=2,uniqueMainSourceFiles=1)
    assert counts({'a':dict(path='p/A.java'),'b':dict(path='q/A.java')})==dict(mainClassDeclarations=2,uniqueMainSourceFiles=2)
    assert counts({'a':dict(path='p/A.java')})==dict(mainClassDeclarations=1,uniqueMainSourceFiles=1)
    try:counts({'a':dict(path=None)})
    except ValueError:pass
    else:raise AssertionError('unknown source unit accepted')
    gdir=BASE/'PG9386-composite-reference-graph-v3';graph=json.loads((gdir/'manifest.json').read_bytes())
    main_raw=(gdir/'main-class-sources.json').read_bytes();assert sha(main_raw)==graph['mainMapSha256'];all_mains=json.loads(main_raw)
    post_path=BASE/'PG9388-composite-reference-post-v1/manifest.json';post_raw=post_path.read_bytes()
    assert sha(post_raw)=='46d1cf32bc0e7ec1ac5882f43250201eb6d23e72acb4c6ef64cea823d9f1087e'
    old=json.loads(post_raw);names=[name.replace('.','/') for receipt in old['receipts'] if receipt['command'][1]=='-p' for name in receipt['command'][4:]]
    assert len(names)==len(set(names))==96
    first=counts({name:all_mains[name] for name in names});assert first==dict(mainClassDeclarations=96,uniqueMainSourceFiles=63)
    current_dir=BASE/'PG9410-reflective25-source-metadata-v2';current_raw=(current_dir/'manifest.json').read_bytes()
    assert sha(current_raw)=='3a091fd42596d8529b93c65147a7045e82824c049d5d507ca024eac08f6d8f13'
    current=json.loads(current_raw);proof_raw=(current_dir/'main-source-proofs.json').read_bytes();assert sha(proof_raw)==current['mainProofsSha256']
    second=counts(json.loads(proof_raw));assert second==dict(mainClassDeclarations=63,uniqueMainSourceFiles=49)
    assert old['independentMainSourceFiles']==first['mainClassDeclarations'] and current['independentMainSourceFiles']==second['mainClassDeclarations']
    fields=dict(PG9388=first,PG9410=second,PG9412=second)
    verify(invocation)
    event=metrics.append('G13_REFLECTIVE25_SOURCE_ONLY_V1','CHECKPOINT',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],
      source=SOURCE,workCategory='ADMIN',correctsEventId='PGPT-20261008-2144',correction='independentMainSourceFiles96 was class declarations96, unique source paths63; preserve original event',
      correctedTechnicalMeasurementUnits=fields,failureIds=['BUG-1750'],acceptedDelta=dict(closedIds=[],reopenedIds=[],criteriaSatisfied=[],evidenceRefs=[]),
      quotaBefore=None,quotaAfter=None,observedSharedPp=None,actualAllocatedPp=None,effortCompletionRate=None,pgptAllComplete=False))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,eventId=event,
          correctedUnitMeasurements=fields,unitFixtureVectors=4,priorManifestSha256=sha(post_raw),currentManifestSha256=sha(current_raw),
          originalManifestsAndEventsUnchanged=True,oldFieldInterpretation='CLASS_DECLARATIONS_NOT_UNIQUE_SOURCE_FILES',
          historicalQualifierCount9400ProtocolSubjectSources=8,protocolEightUniqueSubjectsUnaffected=True,
          targetToolOrTestReplay=0,newSourceRegistrations=0,newAccepted=0,coverage=None,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=event,measurements=fields,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
