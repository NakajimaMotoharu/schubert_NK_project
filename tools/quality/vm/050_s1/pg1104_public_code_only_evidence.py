"""Allowlisted safe evidence only; old compile/activation failures remain failures."""
import hashlib
import json
import os
from pg1082_public_evidence import ROOT,KEYS,OBSERVED
from pg1041_cold_policy_diagnostic import W


def main():
    paths=['pg1092-cold-activation-frozen-v1.safe.json','pg1095-cold-activation-frozen-v2.safe.json',
           'pg1096-stage-v1.safe.json','pg1096-activate-v1.safe.json',
           'pg1098-partial-exchange-preflight-v1/manifest.safe.json','pg1099-partial-exchange-handoff-v1/manifest.safe.json',
           'pg1101-linked-preservation-frozen-v1.safe.json','pg1102-stage-v1.safe.json','pg1102-preserve-v1.safe.json',
           'pg1103-linked-preservation-post-v1/manifest.safe.json','pg1105-stale-atime-guest-fixture-v1/manifest.safe.json']
    extra={'current1068FullSigned','old932FullPreserved','linkedOriginalNineFieldsAclVerified',
           'startupInvalidUnchanged','allResources0','partialPublicationUnchanged','oldBusGone','oldClientsAdvisoryFlocks0',
           'sameReadOnlyPeerSocket','fullOldNewSigned','partialPublicationVerified','oldActorUntouched','signalAttempted',
           'oldNormalClose','fixtureOnly','realCurrentEpochDbUnitsUnmodified','staleAtimeUpdatedWithoutChangingNineContractFields',
           'allFixtureFdsNormalClosed'}
    scopes=[]
    for name in paths:
        raw=(W/name).read_bytes();value=json.loads(raw)
        result={k:v for k,v in value.items()if k in KEYS}
        result.update(privateManifestSha256=hashlib.sha256(raw).hexdigest(),privateEvidenceReference=str(W/name))
        if 'observed'in value:result['observed']={k:v for k,v in value['observed'].items()if k in OBSERVED|extra}
        if 'phases'in value:result['phaseResults']=[{'phase':v['phase'],'actualExit':v['actualExit'],'logSha256':v['logSha256']}for v in value['phases']]
        scopes.append(result)
    if scopes[0]['actualExit']!=1 or scopes[3]['actualExit']!=143 or any(scopes[i]['actualExit']!=0 for i in (1,2,4,5,6,7,8,9,10)):
        raise ValueError('independent actual outcomes required')
    if not all(scopes[9]['observed'][k]for k in ('current1068FullSigned','linkedOriginalNineFieldsAclVerified','allResources0','observerNormalClose')):
        raise ValueError('whole newcurrent independent post required')
    record={'program':'NK-OPS-001','branch':'dev-foundation','currentSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed',
      'preservedOriginalSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','release':'0.1.0-PG1068',
      'manifestSha256':'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',
      'expected':{'artifacts':187,'schema':'028','history':29,'tablesUnchanged':24,'batchRowsUnchanged':594,
        'resourcesAfter':0,'newScopesNormal':True,'oldFailedActivationAccepted':False,'ordinaryRootNotYetAccepted':True},
      'environmentReference':['documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md','documents/400_PGPT/420_環境/424_隔離Linux_PGPT環境構築記録.md'],
      'environment':{'hostKernel':'7.0.0-38-generic','guestKernel':'7.0.0-34-generic','jdk':'25.0.4','python':'3.14.4','maven':'3.9.12','postgresql':'18.6'},
      'scopes':scopes,'bugs':['BUG-1025'],'ykt':['YKT-794'],'ssc':['SSC-249','SSC-250','SSC-251'],
      'testIds':['PT-DEP-1088005','PT-DEP-1091003','PT-DEP-1094001..002','PT-DEP-1097001..003','PT-DEP-1098001..002','PT-DEP-1099001..002','PT-DEP-1100001..002','PT-DEP-1103001','PT-DEP-1105001'],
      'commands':['python3 -B tools/quality/vm/050_s1/'+n for n in ['pg1095_cold_activation_compile_v2.py','pg1096_cold_activation_native_v2.py stage','pg1096_cold_activation_native_v2.py activate','pg1098_partial_exchange_preflight.py','pg1099_partial_exchange_handoff.py','pg1101_linked_preservation_compile.py','pg1102_linked_preservation_native.py stage','pg1102_linked_preservation_native.py preserve','pg1103_linked_preservation_post.py','pg1105_stale_atime_guest_fixture.py']],
      'rerunPolicy':'Completed fixed slots must not be replayed. Old failures retained; new current ordinary Root requires fresh source/run/owner.',
      'acceptedScope':'SSC251 code-only finite publication recovery and linked preservation; no ordinary Root/native/formal acceptance',
      'coverage':'Tooling and limited VM evidence; not new Production four-counter/formal certification',
      'oldFailedResultNormalized':False,'sourceRunScopesKeptSeparate':True,'formalAccepted':False,'wholeWbsAcceptedDelta':0,'secretsIncluded':False}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG1092-1105-cold-code-only'
    out.mkdir();data=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode()
    with(out/'manifest.json').open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':len(scopes),'publicManifestSha256':hashlib.sha256(data).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
