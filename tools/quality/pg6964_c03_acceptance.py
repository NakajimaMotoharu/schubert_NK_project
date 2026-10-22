"""Seal one C03 acceptance from existing original host evidence, never rerun PT."""
import argparse
import copy
import datetime
import json
import os
import platform
import subprocess
from pathlib import Path

import pg6946_c03_current_criteria as config
import pg6962_jms_f02_criteria as prior
import wbs_progress_audit as audit

ROOT, PMO, SOURCE = prior.ROOT, prior.PMO, prior.SOURCE
PRIOR = PMO / '489_当source個別受入_初回九項目.json'
REVIEW = ROOT / 'evidence/01_PT/018_NK-OPS-001/1528_C03_当source設定個別受入matrix.md'
PROOF = prior.BASE / 'PG6946-c03-current-criteria-v1/manifest.json'
HASH = '9695e383d3af6f227e9d01fecc37063faa7f304ad463c8090a7368d808a2546c'
ID = 'WBS-C03'


def scope(task, manifest, inventory):
    prior.require(set(task['ownedArtifacts']) == set(config.OWNED), 'exact two declared C03 artifacts')
    rows = [v for v in inventory['artifacts'] if v['owner'] == ID]
    prior.require(len(rows) == 2 and {v['path']:v['sha256'] for v in rows}
                  == {p:manifest['inputHashes'][p] for p in config.OWNED}, 'all physical C03, no hidden extra')
    prior.require(not task['dependencies'] and not task['sharedClassReferences'], 'unchanged explicit exit dependencies')


def verify(register):
    previous = json.loads(PRIOR.read_bytes())
    prior.verify_register(previous)
    prior.require(register['source'] == SOURCE and register['reviewState'] == 'COMPLETE'
                  and register['acceptedBy'] and register['formalUpdated'] is False
                  and register['wholeEffortCompletionRate'] is None, 'explicit source-specific completed review')
    prior.require(register['priorRegister'] == dict(path=str(PRIOR.relative_to(ROOT)), sha256=prior.sha(PRIOR)),
                  'prior nine register sealed')
    prior.require(register['review'] == dict(path=str(REVIEW.relative_to(ROOT)), sha256=prior.sha(REVIEW)),
                  'actual complete C03 semantic review fixed')
    states = register['records']
    prior.require(set(states) == set(previous['records']) | {ID}
                  and all(states[k] == v for k,v in previous['records'].items()), 'only C03 added; prior nine intact')
    prior.require(register['newAcceptedIds'] == previous['newAcceptedIds'] + [ID]
                  and register['revalidatedIds'] == previous['revalidatedIds'], 'no revalidation counted new')
    prior.require(prior.sha(PROOF) == HASH, 'exact immutable original C03 witness')
    manifest = json.loads(PROOF.read_bytes())
    prior.require(manifest['source'] == SOURCE and manifest['actualExit'] == 0
                  and manifest['testsExecutedByReader'] == 0 and not manifest['wholeReplayed']
                  and manifest['originalQualificationSha256'] == '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731',
                  'genuine qualified original cases, not a new run')
    prior.require(prior.initial.git('origin/main', config.DESIGN) == (ROOT/config.DESIGN).read_bytes()
                  and prior.sha(ROOT/config.DESIGN) == manifest['designSha256'], 'canonical requirements unchanged')
    for path, digest in manifest['inputHashes'].items():
        prior.require(prior.sha(ROOT/path) == digest and prior.initial.git(SOURCE,path) == (ROOT/path).read_bytes(),
                      'current source/Test full bytes equal genuine original input')
    config.validate_templates(*[(ROOT/p).read_text() for p in config.OWNED])
    config.validate_roles((ROOT/config.ROLE_SQL).read_text())
    prior.require([r['testId'] for r in manifest['originalCases']]
                  == ['PT-OPS-PGCFG-'+f'{i:03}' for i in range(1,9)], 'complete eight independent TestIDs')
    prior.require(all(r['method'] == name and r['originalCase']['source'] == SOURCE
                      and r['originalCase']['result'] == 'PASS_ORIGINAL_XML'
                      for r,name in zip(manifest['originalCases'],config.METHODS)), 'every original method really passed')
    task = next(copy.deepcopy(v) for v in json.loads((PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks'] if v['id'] == ID)
    inventory = json.loads((PMO/'485_WBS網羅性・受入対応.json').read_bytes())['currentPhysicalCandidate']
    scope(task, manifest, inventory)
    task['acceptance'] = states[ID]
    audit.check_acceptance(task,SOURCE,states)
    prior.require(states[ID]['evidence'] == [dict(path=str(PROOF.relative_to(ROOT)), sha256=HASH,
                  source=SOURCE, run='PG6930-six-v1', verifiedChecks=manifest['localEvidenceChecks'])],
                  'all criteria backed by exact C03 original evidence, not unrelated proof')
    subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],
                   cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    return dict(actualExit=0,source=SOURCE,currentSourceAccepted=10,newAcceptedThisStage=1,newAcceptedTotal=6,
                revalidated=4,originalCasesReferenced=8,newProductionPt=0,wholeReplayed=False,
                formalUpdated=False,wholeEffortCompletionRate=None,runtimeDeploymentVerified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('register',type=Path)
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    result = verify(json.loads(args.register.read_bytes()))
    if args.record:
        result.update(command=['python3','-B','tools/quality/pg6964_c03_acceptance.py',str(args.register),'--record'],
                      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),
                      os=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
                      head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      toolSha256=prior.sha(Path(__file__)),registerSha256=prior.sha(args.register),reviewSha256=prior.sha(REVIEW),
                      originalManifestSha256=HASH)
        os.umask(0o077)
        out = prior.BASE/'PG6964-c03-acceptance-v1'
        out.mkdir()
        with (out/'manifest.json').open('x') as stream:
            json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2)
            stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
