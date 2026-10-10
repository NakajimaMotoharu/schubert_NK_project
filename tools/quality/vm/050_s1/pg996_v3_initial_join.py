"""Read-only G13.07 initial join; candidates are not contract acceptance.

No production oracle generation, guest mutation, history reset, or PMO writes.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / 'documents/400_PGPT/470_PMO'
V3 = Path('/home/mini/codex/project1/work/PMO/hourly-monitor/wbs-reestimate-v3-PGPT-20261008-PG500.json')
EVENTS = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG996-v3-initial-join-v1'

def read(path):
    return json.loads(path.read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_join(wbs, inventory):
    owners = {x['id']: x for x in wbs['tasks']}
    requirements = []
    for r in inventory['requirements']:
        requirements.append({'id': r['id'], 'owner': r['owner'], 'source': r['source'],
                             'designTrace': r['designTrace'], 'contractAccepted': False})
    artifacts = []
    for a in inventory['artifacts']:
        t = owners.get(a['owner'])
        plan = t.get('evidencePlan', {}) if t else {}
        stem = Path(a['path']).stem
        tests = [p for p in plan.get('candidateTestFiles', []) if Path(p).stem == stem + 'Test']
        artifacts.append({'path': a['path'], 'owner': a['owner'], 'costOwner': a['costOwner'],
                          'present': (ROOT/a['path']).is_file(), 'sameInventoryByte':
                          (ROOT/a['path']).is_file() and digest(ROOT/a['path']) == a['sha256'],
                          'candidateTests': tests, 'designFiles': plan.get('designFiles', []),
                          'specDirectory': plan.get('specDirectory'),
                          'independentOracleVerified': False, 'contractAccepted': False})
    return requirements, artifacts

def main():
    os.umask(0o077)
    v = read(V3)
    assert v['revision'] == 'PMO-remaining-v3-20261010' and len(v['leaves']) == 252
    assert v['remaining_estimate_pp'] == {'low': 310.68, 'base': 586.75, 'high': 1297.64}
    assert not OUT.exists()
    last = json.loads(EVENTS.read_bytes().splitlines()[-1])
    assert last['eventId'] == 'PGPT-20261008-0258'
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    event = dict(last)
    event.update(eventId='PGPT-20261008-0259',previousEventId=last['eventId'],eventType='GROUP_START',
      timeJST=now,groupId='V3_INITIAL_TRACE_AND_COLD_REAUTH',gitHead=head,run='PG996/PG997',
      wbsLeafIds=['WBS-G13.07','WBS-N11'],costRevision=v['revision'],estimateRevisionSha256=digest(V3),
      stage='CONTRACT_FIXTURE',estimateAtGroupStartPp={'low':.85,'base':1.75,'high':3.3},
      stageAllocation={'WBS-G13.07':{'initial':{'low':.6,'base':1,'high':1.8},
         'regions':{'low':.95,'base':1.5,'high':2.75},'final':{'low':.4,'base':.75,'high':1.3}},
         'WBS-N11':{'contract':{'low':.25,'base':.75,'high':1.5},
         'offlineBoot':{'low':.5,'base':1,'high':2},'reauth':{'low':.5,'base':.75,'high':1.5},
         'close':{'low':.25,'base':.25,'high':1}}},
      remainingEstimatePp=v['remaining_estimate_pp'],estimateChangeReason='Approved v3 residual only; original and past estimates retained. Actual VM absent creates cold-boot dependency, not replay of completed routes.',
      quotaBefore={'fetchedAtJST':'2026-10-10T11:40:51+09:00','limitId':'codex','windowDurationMins':10080,
                   'resetsAt':1791987599,'usedPercent':91,'remainingPercent':9,'source':'reset_credit.py status official read'},
      quotaAfter=None,observedSharedPp=None,sameQuotaWindow=True,actualAllocatedPp=None,
      resetPolicy='weekly >1 continue; <=3 preserve; <=1 one designated credit after durable checkpoint; fresh receipt and limits required',
      tokenMeasurementIds=['aa2d0f187753f99927193b1cedc1829f17fbb488d23b2376fe326976827454dc'],tokenTotals=None,
      acceptedDelta={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},
      technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[]},
      actualPaths=[],failureIds=[],attempt=None,attemptResult=None,retryCause=None,stopReason=None,
      unaccepted=['G13 global independent oracle joins','current cold boot','Inspector current native','QA051 final L01'],
      nextCommand='PG996 initial join then new-only isolated PG997 offline preservation and management boot; never reuse old runtime/permit.',
      modelRequested='gpt-6.1-sol',reasoningRequested='high',modelObserved=None,reasoningObserved=None,
      modelVerificationMethod='User requested configuration; app setting not inspected',formalRunDelta=None,pgptAllComplete=False)
    with EVENTS.open('ab') as f:
        f.write((json.dumps(event,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    w = read(DOC/'481_PGPT詳細WBS.json'); i = read(DOC/'485_WBS網羅性・受入対応.json')
    req, art = build_join(w,i)
    OUT.mkdir(parents=True)
    spec_candidates = []
    for p in sorted((ROOT/'evidence/01_PT').rglob('*.md')):
        ids = sorted(set(re.findall(r'\bPT-[A-Z0-9]+-[A-Z0-9-]+',p.read_text())))
        if ids: spec_candidates.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'testIds':ids,
                                       'mapping':'CANDIDATE_ONLY_NOT_ORACLE_ACCEPTANCE'})
    record = {'run':'PG996-v3-initial-join-v1','timeJST':now,'head':head,
      'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97',
      'estimateRevision':v['revision'],'estimateSha256':digest(V3),'requirements':req,'artifacts':art,
      'specCandidates':spec_candidates,'formalAccepted':False,'wholeAcceptedDelta':0,
      'focusedOracleJoin':[
        {'testId':'PT-DEP-997001','owner':'WBS-N11','design':'SS343 SSC165/174; SS353',
         'expected':'Existing saved disk stable, private copy exact SHA; all QEMU/disk owners/SSH absent before management-only boot; old /run restoration and business start zero.',
         'evidence':'PG997 offline and cold-boot current observation','status':'PLANNED_NOT_RUN'},
        {'testId':'PT-DEP-998001','owner':'WBS-N11','design':'SS343 SSC165/174; SS342',
         'expected':'New boot identity; canonical ten Unit cold properties/kernel empty; current 187 signed payload and 24 tables match preserved durable after-image, ignore tmpfs inode equivalence across boot; no old permit or native synthesized.',
         'evidence':'new readonly current snapshot','status':'PLANNED_NOT_RUN'},
        {'testId':'PT-DEP-999001','owner':'WBS-N04','design':'SS342/343/352; P00404',
         'expected':'Inspector may run only within approved live root ownership and deadline; same-day ALREADY and successful old progress retained. New-day fixture must not erase history or borrow expired owner.',
         'evidence':'current source/authority/progress join','status':'CONTRACT_AUDIT_PENDING'}],
      'gaps':{'missingArtifact':sum(not a['present'] for a in art),
              'changedInventoryByte':sum(not a['sameInventoryByte'] for a in art),
              'noDirectCandidateTest':sum(not a['candidateTests'] for a in art),
              'independentOracleJoinsUnverified':len(art)},
      'initialJoinMeaning':'Initial owner/requirement/candidate TestID join and explicit missing oracle work; no regex/presence based global acceptance. Region-specific independent matrix and final delta remain.'}
    target = OUT/'manifest.json'
    with target.open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'run':record['run'],'requirements':len(req),'artifacts':len(art),
      'specCandidates':len(spec_candidates),'gaps':record['gaps'],'manifestSha256':digest(target),
      'wholeAcceptedDelta':0,'eventId':event['eventId']}))

if __name__ == '__main__':
    main()
