"""Durable current ownership checkpoint, not a stop or normal-close assertion."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg4420_shared_manager_full import ROOT, W, SOURCE


def main():
    actors=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():continue
        try:
            argv=(path/'cmdline').read_bytes();parts=argv.split(b'\0')
            if b'tools/quality/pg4462_failed_unused_dispatch.py' not in parts or b'inspect' not in parts:continue
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            actors.append({'pid':int(path.name),'ppid':int(fields[1]),'ticks':int(fields[19]),'state':fields[0],
                           'argvSha256':hashlib.sha256(argv).hexdigest()})
        except(FileNotFoundError,ProcessLookupError):continue
    if len(actors)!=1:raise ValueError('one original live inspect wrapper required; do not infer termination')
    diagnosis=json.loads((W/'pg4472-reference-fields-diagnosis-v1/manifest.safe.json').read_bytes())
    if diagnosis['actualExit']!=0:raise ValueError('actual fresh current owner diagnosis required')
    checkpoint={'timeJST':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'dirty':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
        'productionCandidateSource':SOURCE,'deployedSource':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
        'candidateRelease':'PG4432','candidateBom':'93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',
        'deployedBom':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
        'guestBoot':'79a3260a-e16d-42bf-942a-b914ed144c28','originalExec':20650,'originalActualExit':None,
        'hostActors':actors,'guestActors':diagnosis['result']['actors'],'guestPeers':diagnosis['result']['peers'],
        'guestFlocks':diagnosis['result']['flocks'],'sameFrozenFiles':142,'sameArtifactTools':'pg4444-failed-current-unused-tools-v4',
        'originalStageActualExit':1,'existingInputStageConsumerActualExit':0,'stageReplayAllowed':False,
        'candidatePlaced':False,'candidatePublished':False,'oldScopesNormal':False,'formalAccepted':False,
        'formalTests':1964,'formalScopes':53,'effortCompletion':None,'QA051final':'HELD',
        'next':'Do not re-run inspect20650/stage87076 or hotpatch142. Fresh reauthenticate exact Java827198/t16494387 and Python827230/t16494598, DB827228, M/A and10 metadataRefs; capture full actor/FD/authority and all24/original/Backup/native58/startup37/189/32 twice. Necessary SSC297 exact current pre-operation metadata-pair owned handoff, independent no-action proof/design-only main, normal owned TERM once in proper order retaining10Ref continuity; original transport failure and old unknown remain unknown; independent all resources/current data post. Then new artifact caller set(PARENT_FIELDS), actual sealed show positive/negative test, current7bb host compile, one new inspect/newonlySAVE, thenunused/RO/publication/newRoot/native/quality.',
        'quotaUsedPercent':65,'quotaRemainingPercent':35,'quotaObservedAt':'2026-10-17T00:38 JST fresh tool','resetCredits':0,
        'measurementNote':'Historical quota in this checkpoint; re-query before new activity. No quota-to-token conversion.',
        'ordinaryUnitOrBusinessMutationsIssued':0,'allProtectedOriginalsStashAndBaselinePreserved':True}
    os.umask(0o077);path=W/'pg4474-inspect-unknown-checkpoint.json'
    with path.open('x')as output:json.dump(checkpoint,output,sort_keys=True);output.flush();os.fsync(output.fileno())
    print(json.dumps({'checkpoint':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'hostActors':actors,'originalJobUnknown':True}))


if __name__=='__main__':
    main()
