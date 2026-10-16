"""Journalled mechanical source bridge after exact17/51 proof; zero new acceptance/cost."""
import argparse
import inspect
import types
import pg3544_current_wbs_source_switch as previous
import pg3916_current_criteria_revalidation as current
import pg3542_current_criteria_revalidation as helpers
from pg1446_current_cold_stage import W

review=types.SimpleNamespace(**{**helpers.__dict__,**current.__dict__})
ROOT=review.ROOT;PMO=review.PMO;SOURCE=review.SOURCE
OUT=W/'pg3918-current-wbs-source-switch-v1'
PROOF=review.PUBLIC/'manifest.json'
NAMES=previous.NAMES;MUTATED=previous.MUTATED
RUNTIME={'WBS-N05','WBS-N06','WBS-N07','WBS-N08','WBS-N09','WBS-N10','WBS-N14'}


def candidates(texts,proof):
    raw=inspect.getsource(previous.candidates)
    pairs=[
      ('PG3542-current-criteria-revalidation-v1','PG3916-current-criteria-revalidation-v1'),
      ('current3712/source','current3714/source'),
      ("artifact['sha256']==change['oldSha256']and artifact['owner']=='WBS-P006-02'","artifact['sha256']==change['oldSha256']and artifact['owner']==change['owner']"),
      ('one unaccepted Main change only','exact original ownership of all260 source-bound changes'),
      ("'BUG1299/4856b3fca; actual3712/545/1643/current native10points9streams; individual Outbox scope remains NOT_ACCEPTED'","'Source7fff/hygiene260; genuine3714/545/1643/native20points18streams; existing17/51 individually revalidated, all other scopes remain unaccepted'"),
      ("measurement=review.read(ROOT/review.MEASUREMENT);data=group_coverage(measurement)","measurement=review.read(ROOT/review.MEASUREMENT);measurement={**measurement,'remaining':{k:sum(v[k]['missed']for v in measurement['moduleCounters'].values())for k in ('LINE','METHOD','CLASS','BRANCH')}};data=group_coverage(measurement)"),
      ("elif row['id']in RUNTIME or row['id']=='WBS-CHR-A01':","elif row['id']in RUNTIME:"),
      ('evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3534-current-root-owned-native-v1/manifest.json','evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3898-current-resume-lifecycle-v1/manifest.json'),
      ('PG3534-current-root-owned-native-v1','PG3898-current-resume-lifecycle-v1'),
      ('Olda9 stage is preserved, not yet fully re-proved on4856; current Root DONE alone does not prove intent/runtime retirement','Historical stage retained; this source bridge does not yet join that separate current-stage or CHR proof, no live authority transferred'),
      ('measurement[\'run\'],3712,545,1643','measurement[\'run\'],3714,545,1643'),
      ('Current4856 actual3712/545/1643 plus eligible native10points/latest9; olda9/native28 excluded.','Current7fff actual3714/545/1643 plus eligible same-source20points/latest18; all foreign-source streams excluded.'),
      ('currentSourceRevalidation20261016','currentSourceRevalidation20261016PG3918'),
      ("'physicalChanges':1,'measurementNativePoints':10,'latestNativeStreams':9","'physicalChanges':260,'measurementNativePoints':20,'latestNativeStreams':18"),
      ("'A01MeasuredNotFullGate':True,'N09IntentAndN14RetirementStillNeedCurrentProof':True","'A01CurrentProofJoined':False,'N09IntentAndN14RuntimeLimitedStageVerified':True,'limitedRuntimeStagesOnlyNotLeafAcceptance':True")]
    for old,new in pairs:
        if old not in raw:raise ValueError('exact source bridge boundary missing '+old[:90])
        raw=raw.replace(old,new)
    values={**previous.__dict__,'review':review,'ROOT':ROOT,'PMO':PMO,'SOURCE':SOURCE,'OUT':OUT,'PROOF':PROOF,'RUNTIME':RUNTIME}
    exec(compile(raw,'<exact current source and existing criterion mechanical bridge>','exec'),values)
    return values['candidates'](texts,proof)


def namespace():
    values={**previous.__dict__,'review':review,'ROOT':ROOT,'PMO':PMO,'SOURCE':SOURCE,'OUT':OUT,'PROOF':PROOF,'RUNTIME':RUNTIME,'candidates':candidates}
    for function in [previous.stage,previous.apply]:exec(compile(inspect.getsource(function),'<new-only journalled current source bridge>','exec'),values)
    return values


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['stage','apply']);raise SystemExit(namespace()[parser.parse_args().action]())
