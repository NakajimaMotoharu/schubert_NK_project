"""Same-source actual18-stream XML projection; technical session IDs hash-redacted only."""
import datetime
import json
import os
from pathlib import Path
import types
import pg3280_wbs_current_source as base
from pg1446_current_cold_stage import W
from pg3564_current_browser_resume_sources import SOURCE

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg3672-current-native-public-projection-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3632-current-native-measurement-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    native=json.loads((W/'pg3632-current-browser-native-qualified-v1/manifest.safe.json').read_bytes());full=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes());n=native['result'];f=full['result']
    if not(native['actualExit']==full['actualExit']==0 and n['productionSource']==f['productionSource']==SOURCE and n['classByteMismatch']==0 and n['currentNativeStreams']==18 and n['validatedNativePoints']==20 and n['historicalSourceNativeImported']is False and f['tests']==3712 and f['mainClasses']==1643):
        raise ValueError('actual current eighteen-stream and same3712 source required')
    fetch=types.FunctionType(base.fetch_fixed.__code__,{**base.__dict__,'REMOTE':'/home/mini/schubert-nk-pgpt/runs/PG3632-native-v1'})
    manifest=out/'manifest.private.json';fetch('manifest.safe.json',manifest)
    if base.sha(manifest.read_bytes())!=native['manifestSha256']or json.loads(manifest.read_bytes())!=n:raise ValueError('immutable original current native result required')
    projections={}
    for module in base.MODULES:
        p=out/(module+'-union.xml');fetch(p.name,p);raw=p.read_bytes()
        if base.sha(raw)!=n['xmlHashes'][module]:raise ValueError('immutable current original XML hash required')
        projections[module]=base.redact_report(raw,n['moduleCounters'][module])
    PUBLIC.mkdir(parents=True);modules=[]
    for module,(raw,redaction)in projections.items():
        target=PUBLIC/'coverage'/module/'site/jacoco/jacoco.xml';target.parent.mkdir(parents=True)
        with target.open('xb')as stream:stream.write(raw)
        modules.append({'module':module,'coverageXmlSha256':base.sha(raw),'rawCoverageXmlSha256':n['xmlHashes'][module],'pt':f['modules'][module],'redaction':redaction})
    value={'actualExit':0,'productionSource':SOURCE,'sourceSnapshot':f['sourceSnapshot'],'run':'PG3632-current-native-measurement-v1','kind':'CURRENT_SOURCE_TECHNICAL_PROJECTION_NOT_ACCEPTANCE','FES':0,'staticIssues':0,'staticIssuesScope':'EXISTING_SIX_MODULE_COMPILER_NULLAWAY_SPOTBUGS_ONLY_F03_NOT_ACCEPTED','F03Accepted':False,'PMDRaw':2217,'CheckstyleRaw':645,'tests':3712,'suites':545,'mainClasses':1643,'nativeStreams':n['currentNativeStreams'],'validatedNativePoints':n['validatedNativePoints'],'coverageRoot':str((PUBLIC/'coverage').relative_to(ROOT)),'modules':modules,'moduleCounters':n['moduleCounters'],'gain':n['gain'],'remaining':{k:sum(v[k]['missed']for v in n['moduleCounters'].values())for k in base.COUNTERS},'originalNativeManifestSha256':native['manifestSha256'],'fullPrivateReceiptSha256':base.sha((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes()),'nativePrivateReceiptSha256':base.sha((W/'pg3632-current-browser-native-qualified-v1/manifest.safe.json').read_bytes()),'oldSourceNativeImported':False,'acceptedLeafDelta':0,'formalAccepted':False,'effortPercent':None,'canonicalAcceptance':{'source':SOURCE,'accepted':17,'total':190,'automaticSourceRebinding':False},'inventoryBindingApplied':False,'scopeChanged':False,'mavenReissued':False,'vmActions':0,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with(PUBLIC/'manifest.json').open('x')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),'sha256':base.sha((PUBLIC/'manifest.json').read_bytes()),'source':SOURCE,'modules':6,'remaining':value['remaining'],'acceptedLeafDelta':0,'inventoryBindingApplied':False}));return 0


if __name__=='__main__':raise SystemExit(main())
