"""Only current PG690 eight fresh streams plus frozen same-source PG680 host."""
import json
from pathlib import Path
import subprocess
from pg644_native_counter import code as previous_code,CATALOG as PREVIOUS_CATALOG
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def code(hashes,proof,seals):
    assert proof['actualExit']==0 and proof['productionSource']=='9bd50536f692610036a0ed8b83e0a8b35fe2a66f'
    assert proof['batchRun']=='8633b77f-77dc-4a78-88b4-41165f159b43'
    assert proof['genuineCompletion']['genuineRootDone']and proof['genuineCompletion']['genuinePid1StartDone']
    end=proof['genuineCompletion']['endMonotonicUs'];assert type(end)is int and 119288459330<=end<=121088459330
    return replace(previous_code(hashes),(
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('pg642-native-stop-v1','pg696-native-stop-v1'),
        ('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',seals['before.private.json']),
        ('011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c',seals['after.private.json']),
        ('104329','122726'),('293d218b06454bd1a8ff350bb93de2d5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('103062293730','119288459330'),('104759573609',str(end)),
        ('pg643-terminal-final-v2','pg697-terminal-final-v1'),
        ('pg630-retention-factory-six-host-v1','pg680-owner-six-host-v1'),
        ('067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b','b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'),
        ("tests']==3468","tests']==3489"),
        ('pg644-current-eight-native-v1','pg698-current-eight-native-v1'),('PG644-current-eight-native-v1','PG698-current-eight-native-v1'),
    ))


def catalog(before_sha):
    assert type(before_sha)is str and len(before_sha)==64
    return replace(PREVIOUS_CATALOG,(
        ('pg642-native-stop-v1','pg696-native-stop-v1'),
        ('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',before_sha),
    ))


def main():
    assert(W/'pg697-terminal-final-v1.exit').read_bytes()==b'0\n'
    post=json.loads((W/'pg697-terminal-final-v1.safe.json').read_text())
    proof=json.loads((W/'pg693-completed-readonly-v1.safe.json').read_text())
    seals={k:v['sha256']for k,v in post['proofHashes'].items()}
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    hashes=json.loads(subprocess.check_output(ssh,input=catalog(seals['before.private.json']).encode(),timeout=30));assert len(hashes)==8
    env={'__file__':str(R/'pg698_native_counter.py'),'__name__':'current_source_eight_native'}
    exec(compile(code(hashes,proof,seals),'<new source genuine native/host qualifications>','exec'),env);env['main']()


if __name__=='__main__':main()
