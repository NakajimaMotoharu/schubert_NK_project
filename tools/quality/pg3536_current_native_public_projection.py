"""Hash-qualified current native XML projection, not source/acceptance rebinding."""
import datetime
import json
import os
from pathlib import Path
import types
import pg3280_wbs_current_source as base
from pg1446_current_cold_stage import W
from pg3520_outbox_owned_sources_v2 import SOURCE

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg3536-current-native-public-projection-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3532-current-native-measurement-v3'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    native=json.loads((W/'pg3532-outbox-current-native-qualified-v3/manifest.safe.json').read_bytes())
    full=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())
    n=native['result'];f=full['result']
    if native['actualExit']!=0 or full['actualExit']!=0 or n['productionSource']!=SOURCE or f['productionSource']!=SOURCE:
        raise ValueError('current same-source actual authorities required')
    if n['productionSource']!=SOURCE or n['classByteMismatch']!=0 or n['oldNativeImported']is not False or f['tests']!=3712 or f['mainClasses']!=1643:
        raise ValueError('exact current qualification required')
    fetch=types.FunctionType(base.fetch_fixed.__code__,{**base.__dict__,'REMOTE':'/home/mini/schubert-nk-pgpt/runs/PG3532-native-v3'})
    manifest=out/'manifest.private.json';fetch('manifest.safe.json',manifest)
    if base.sha(manifest.read_bytes())!=native['manifestSha256']or json.loads(manifest.read_bytes())!=n:
        raise ValueError('original immutable native result required')
    projections={}
    for module in base.MODULES:
        rawpath=out/(module+'-union.xml');fetch(rawpath.name,rawpath);raw=rawpath.read_bytes()
        if base.sha(raw)!=n['xmlHashes'][module]:raise ValueError('original raw XML hash required')
        projections[module]=base.redact_report(raw,n['moduleCounters'][module])
    PUBLIC.mkdir(parents=True);modules=[]
    for module,(raw,redaction)in projections.items():
        target=PUBLIC/'coverage'/module/'site/jacoco/jacoco.xml';target.parent.mkdir(parents=True)
        with target.open('xb')as stream:stream.write(raw)
        modules.append({'module':module,'coverageXmlSha256':base.sha(raw),'rawCoverageXmlSha256':n['xmlHashes'][module],'pt':f['modules'][module],'redaction':redaction})
    value={'actualExit':0,'productionSource':SOURCE,'sourceSnapshot':f['sourceSnapshot'],'run':'PG3532-current-native-measurement-v3',
           'kind':'CURRENT_SOURCE_TECHNICAL_PROJECTION_NOT_ACCEPTANCE','FES':0,'staticIssues':0,
           'tests':3712,'suites':545,'mainClasses':1643,'nativeStreams':9,'validatedNativePoints':10,
           'coverageRoot':str((PUBLIC/'coverage').relative_to(ROOT)),'modules':modules,
           'moduleCounters':n['moduleCounters'],'gain':n['gain'],
           'remaining':{k:sum(v[k]['missed']for v in n['moduleCounters'].values())for k in base.COUNTERS},
           'originalNativeManifestSha256':native['manifestSha256'],'fullPrivateReceiptSha256':base.sha((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes()),
           'nativePrivateReceiptSha256':base.sha((W/'pg3532-outbox-current-native-qualified-v3/manifest.safe.json').read_bytes()),
           'oldSourceNativeImported':False,'acceptedLeafDelta':0,'formalAccepted':False,'effortPercent':None,
           'historicalAcceptance':{'source':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','accepted':17,'total':190,'automaticSourceRebinding':False},
           'inventoryBindingApplied':False,'scopeChanged':False,'mavenReissued':False,'vmActions':0,
           'currentSourceRevalidationPending':'All previously accepted individual criteria and dependencies must be revalidated before canonical WBS source switch; no hash-only refresh.',
           'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with(PUBLIC/'manifest.json').open('x')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    summary={'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),'sha256':base.sha((PUBLIC/'manifest.json').read_bytes()),'source':SOURCE,'modules':6,'remaining':value['remaining'],'acceptedLeafDelta':0,'inventoryBindingApplied':False}
    with(out/'projection.safe.json').open('x')as stream:json.dump(summary,stream,sort_keys=True)
    print(json.dumps(summary));return 0


if __name__=='__main__':raise SystemExit(main())
