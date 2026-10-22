"""One subleaf at a new common component source; original Production reuse explicit."""
import argparse
import copy
import json
import os
import subprocess
from pathlib import Path

import pg6962_jms_f02_criteria as old
import pg6966_chr_adapter_host as host
import wbs_progress_audit as audit

SOURCE='3c70db39377cee751d7ecd12bb439c447e0c61c0'
ID='WBS-P020-01.01'
Q=host.BASE/'PG6980-chr-path-qualification-v1/manifest.json'
STATIC=host.BASE/'PG6982-chr-static-review-v1/manifest.json'
OUT=host.BASE/'PG6984-chr-adapter-acceptance-v1'
DOCS=('documents/300_SS/350_運用・品質/355_Characterization Test実行準備・PG開始gate.md',
      'documents/200_UI/260_引継ぎ・監査/264_現行互換性Characterization Test仕様.md')


def evidence():
    previous=json.loads((old.PMO/'489_当source個別受入_初回九項目.json').read_bytes())
    old.verify_register(previous)
    host.require(host.sha(Q)=='0bbc80f788ac9c26caada7f363415a803aa6cef3796222d519467d6d60e34631'
                 and host.sha(STATIC)=='0e6fc7a9d14b985a19d9d3e506e7f9b96f569396bfba78d1bf838a158ea0525b', 'exact actual host qualification/static review')
    q,static=[json.loads(p.read_bytes()) for p in (Q,STATIC)]
    host.require(q['source']==static['source']==SOURCE and q['actualExit']==static['actualExit']==0
                 and static['unknownRows']==static['suppressedRows']==0 and q['tests']==44
                 and q['crcClassMismatch']==0 and q['originalBaselineUnchanged'], 'all current source quality without raw exit laundering')
    host.require(host.sha(host.ROOT/static['semanticReviewPath'])==static['semanticReviewSha256'], 'complete frozen semantic findings review')
    docs=DOCS
    for path in docs:host.require(old.initial.git('origin/main',path)==(host.ROOT/path).read_bytes(),'canonical approved oracle, no baseline change')
    subprocess.run(['git','diff','--exit-code',host.SOURCE,SOURCE,'--','src','pom.xml','.mvn','mvnw','tools/quality/static'],
                   cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    changed=subprocess.check_output(['git','diff','--name-only',host.SOURCE,SOURCE,'--','program/characterization'],cwd=host.ROOT,text=True).splitlines()
    host.require(set(changed)=={'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java',
                                'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java'},'targeted one Main/one Test delta only')
    parent=next(v for v in json.loads((old.PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks'] if v['id']=='WBS-P020-01')
    inventory=json.loads((old.PMO/'485_WBS網羅性・受入対応.json').read_bytes())['currentPhysicalCandidate']
    prior={a['path']:a['sha256'] for a in inventory['artifacts'] if a['owner']=='WBS-P020-01'}
    host.require(set(prior)==set(parent['ownedArtifacts']) and len(prior)==4,'all parent four sources, no owner/scope removed')
    overlay={p:dict(priorSha256=prior[p],currentSha256=q['sourceInputs'][p],source=SOURCE,owner='WBS-P020-01',additionalBudgetPp=0)
             for p in parent['ownedArtifacts']}
    for p,row in overlay.items():host.require(host.sha(host.ROOT/p)==row['currentSha256'] and old.initial.git(SOURCE,p)==(host.ROOT/p).read_bytes(),'whole current parent source fixed')
    return dict(actualExit=0,source=SOURCE,qualifiedProductionSource=host.SOURCE,productionSourceRun='PG6930-six-v1',
                commonSourceRun='PG6976-chr-path-green-v1',commonQualification=dict(path=str(Q.relative_to(host.ROOT)),sha256=host.sha(Q)),
                commonStaticReview=dict(path=str(STATIC.relative_to(host.ROOT)),sha256=host.sha(STATIC)),
                F02OriginalAcceptance=previous['records']['WBS-F02'],F02OriginalSource=host.SOURCE,F02NewSourceBinding=SOURCE,
                F02SixModuleFullInputByteDelta=0,originalSixReplayed=False,componentScopeOverlay=overlay,
                historical485Unchanged=True,oldE7TenRegisterPreserved=True,formalUpdated=False,wholeEffortCompletionRate=None,
                canonicalDesigns={p:host.sha(host.ROOT/p) for p in docs},reviewChecks=[ID+':deliverable',ID+':quality',
                    'WBS-F02:contract','WBS-F02:scope','WBS-F02:quality'])


def verify(register):
    host.require(register['source']==SOURCE and register['reviewState']=='COMPLETE'
                 and register.get('acceptedBy') and register['formalUpdated'] is False
                 and register['wholeEffortCompletionRate'] is None and register['parentAccepted'] is False
                 and register['newOriginal190Item']==0,'explicit limited new component source, not parent/global completion')
    path=host.ROOT/register['witness']['path'];host.require(host.sha(path)==register['witness']['sha256'],'source binding witness exact')
    host.require(path == OUT/'manifest.json' and host.sha(path)=='acfd9e9c20c8acbb80c63dff96fd21d5c8bde8c1caa8e3f6a09fb8cb34f572e3',
                 'actual independently completed bounded proof, not another self-asserted document')
    proof=json.loads(path.read_bytes());host.require(proof['actualExit']==0 and proof['source']==SOURCE,'genuine complete source binding')
    states=register['records'];host.require(set(states)=={ID,'WBS-F02'},'only new subleaf and necessary byte reauthentication, not old17 rebase')
    tasks=json.loads((old.PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks']
    children=json.loads((old.PMO/'484_WBSコスト枠・細分化.json').read_bytes())['children']
    for rid in (ID,'WBS-F02'):
        task=next(copy.deepcopy(t) for t in tasks+children if t['id']==rid)
        task['acceptance']=states[rid];audit.check_acceptance(task,SOURCE,states)
        checks=[c['id'] for c in task['acceptanceChecks']]
        host.require(states[rid]['evidence']==[dict(path=str(path.relative_to(host.ROOT)),sha256=host.sha(path),
                     source=SOURCE,run='PG6976-chr-path-green-v1',verifiedChecks=checks)],'exact criterion evidence and actual current common run')
    host.require(register['newAcceptedIds']==[ID] and register['revalidatedDependencyIds']==['WBS-F02'], 'revalidated F02 not new gain')
    for p,row in proof['componentScopeOverlay'].items():host.require(host.sha(host.ROOT/p)==row['currentSha256'],'no source changed after qualification')
    for p,h in proof['canonicalDesigns'].items():host.require(old.initial.git('origin/main',p)==(host.ROOT/p).read_bytes() and host.sha(host.ROOT/p)==h,'canonical requirements remain exact')
    old_ten='documents/400_PGPT/470_PMO/490_当source個別受入_C03追加.json'
    host.require(old.initial.git('d07905c0f',old_ten)==(host.ROOT/old_ten).read_bytes(),'previous ten original register preserved byte-for-byte')
    subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],
                   cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    return dict(actualExit=0,newAcceptedSubleaf=1,parentAccepted=False,additionalF02Revalidation=1,
                commonSource=SOURCE,qualifiedProductionSource=host.SOURCE,newOriginal190Item=0,formalUpdated=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',type=Path);args=parser.parse_args()
    if args.register:print(json.dumps(verify(json.loads(args.register.read_bytes()))));return
    value=evidence();os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=SOURCE,manifestSha256=host.sha(OUT/'manifest.json'),accepted=0)))


if __name__=='__main__':main()
