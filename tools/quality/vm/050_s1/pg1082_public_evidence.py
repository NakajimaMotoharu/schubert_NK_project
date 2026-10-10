"""Publish allowlisted sanitized scope results, never private logs/rows/credentials."""
import hashlib
import json
import os
from pathlib import Path
from pg1041_cold_policy_diagnostic import W

ROOT=Path(__file__).resolve().parents[4]
KEYS=frozenset(('run','action','actualExit','operatorSource','productionSource','candidateSource',
 'startedUTC','completedUTC','scriptSha256','logSha256','privateLogSha256','candidateManifestSha256',
 'manifestSha256','signatureSha256','signatureVerified','artifacts','mainClasses','changedClasses',
 'guestMutations0','formalAccepted','unusedColdCandidatePlaced'))
OBSERVED=frozenset(('source','boot','oldParentGone','oldChildGone','allOldClientsAdvisoryAndFlocks0',
 'allOriginalsUnchangedTwice','allTenColdFull32','observerNormalClose','oldOperationNormalClose',
 'childExitUnknown','signalsAttempted','reservationDurable','beforePrivateSha256','afterPrivateSha256',
 'sameAll24OriginalsTwice','exactPreparedNamespaceTwice','allClientsAdvisoryAndFlocks0','oldActorsGone',
 'payloadHostReadonly','startupEpochAndRequestsEmpty','observerRefsNormalClose',
 'unusedCandidateFullPostVerified','candidateNotActivated'))


def main():
    paths=['pg1068-candidate-build-v1.safe.json','pg1077-cold-candidate-tree-preflight-v1/manifest.safe.json',
           'pg1078-cold-candidate-tree-handoff-v1/manifest.safe.json','pg1076-place-v1.safe.json',
           'pg1080-cold-candidate-frozen-v3.safe.json','pg1081-stage-v1.safe.json',
           'pg1081-place-v1.safe.json','pg1082-cold-unused-candidate-post-v1/manifest.safe.json']
    scopes=[]
    for name in paths:
        raw=(W/name).read_bytes();value=json.loads(raw)
        safe={k:v for k,v in value.items()if k in KEYS}
        safe['privateManifestSha256']=hashlib.sha256(raw).hexdigest()
        safe['privateEvidenceReference']=str(W/name)
        if 'observed'in value:safe['observed']={k:v for k,v in value['observed'].items()if k in OBSERVED}
        scopes.append(safe)
    if scopes[3]['actualExit']!=143 or any(scopes[i]['actualExit']!=0 for i in (1,2,4,5,6,7)):
        raise ValueError('separate actual results required')
    if not scopes[-1]['observed']['unusedCandidateFullPostVerified']:
        raise ValueError('independent whole post required')
    record={'program':'NK-OPS-001','branch':'dev-foundation',
      'environment':{'hostKernel':'Linux 7.0.0-38-generic','guestKernel':'Linux 7.0.0-34-generic',
        'jdk':'25.0.4+7-1-26.04-Ubuntu','python':'3.14.4','maven':'3.9.12','database':'PostgreSQL18.6',
        'versionProvenance':'fresh host/guest uname/java/python and421424 fixed installed toolchain'},
      'expected':{'currentSourceUnchanged':'40ef6e894573d2ffab1d1732124960f9c98d5f97',
        'candidateSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','artifacts':187,'tablesUnchanged':24,
        'originalBatchRowsUnchanged':594,'resourcesAfter':0,'startupEmpty':True,'newScopesNormal':True},
      'executionCommands':['python3 -B tools/quality/vm/050_s1/pg1068_stream_candidate_build.py',
        'python3 -B tools/quality/vm/050_s1/pg1077_cold_candidate_tree_preflight.py',
        'python3 -B tools/quality/vm/050_s1/pg1078_cold_candidate_tree_handoff.py',
        'python3 -B tools/quality/vm/050_s1/pg1080_cold_candidate_compile_v3.py',
        'python3 -B tools/quality/vm/050_s1/pg1081_cold_candidate_native_v3.py stage',
        'python3 -B tools/quality/vm/050_s1/pg1081_cold_candidate_native_v3.py place',
        'python3 -B tools/quality/vm/050_s1/pg1082_cold_unused_candidate_post.py'],
      'rerunPolicy':'Recorded commands are completed fixed slots; do not replay. New slots/source required.',
      'testIds':['PT-DEP-1067001..003','PT-DEP-1069001..006',
      'PT-DEP-1077001..004','PT-DEP-1078001','PT-DEP-1071001..002'],
      'productionSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97',
      'unusedCandidateSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed',
      'candidateRelease':'0.1.0-PG1068','scopes':scopes,
      'bugs':['BUG-1023','BUG-1024'],'ykt':['YKT-792','YKT-793'],'ssc':['SSC-247','SSC-248'],
      'acceptedScope':'unused signed candidate placement and independent post only',
      'sourceRunScopesKeptSeparate':True,'oldFailedResultNormalized':False,
      'coverage':'tooling qualification only; no new Production/native or formal counters',
      'formalAccepted':False,'wholeWbsAcceptedDelta':0,'currentActivated':False,
      'environmentReference':['documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md',
       'documents/400_PGPT/420_環境/424_隔離Linux_PGPT環境構築記録.md'],
      'secretsIncluded':False}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG1068-1082-cold-unused-candidate'
    out.mkdir()
    encoded=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode()
    with(out/'manifest.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'publicManifestSha256':hashlib.sha256(encoded).hexdigest(),
      'scopes':len(scopes),'oldFailedScope':143,'formalAccepted':False}))


if __name__=='__main__':main()
