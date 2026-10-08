"""Qualify only eight fresh new-normal streams plus frozen same-source host."""
import json
from pathlib import Path
import subprocess
from pg644_native_counter import code as previous_code,CATALOG as PREVIOUS_CATALOG

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def code(hashes,proof,seals):
    assert proof['actualExit']==0 and proof['batchRun']=='601297d0-a8ba-47da-852b-0ffeae409965'
    assert proof['genuineCompletion']['genuineRootDone']and proof['genuineCompletion']['genuinePid1StartDone']
    end=proof['genuineCompletion']['endMonotonicUs'];assert type(end)is int and 107901545407<=end<=109701545407
    raw=previous_code(hashes)
    for old,new in (
        ('pg642-native-stop-v1','pg655-native-stop-v1'),
        ('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',seals['before.private.json']),
        ('011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c',seals['after.private.json']),
        ('104329','111752'),('293d218b06454bd1a8ff350bb93de2d5','095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('103062293730','107901545407'),('104759573609',str(end)),
        ('pg643-terminal-final-v2','pg656-terminal-final-v1'),
        ('pg644-current-eight-native-v1','pg657-normal-eight-native-v1'),('PG644-current-eight-native-v1','PG657-normal-eight-native-v1'),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


def catalog(before_sha):
    assert type(before_sha)is str and len(before_sha)==64
    return PREVIOUS_CATALOG.replace('pg642-native-stop-v1','pg655-native-stop-v1').replace('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',before_sha)


def main():
    assert(W/'pg656-terminal-final-v1.exit').read_bytes()==b'0\n'
    post=json.loads((W/'pg656-terminal-final-v1.safe.json').read_bytes())
    proof=json.loads((W/'pg653-completed-readonly-v1.safe.json').read_bytes())
    seals={k:v['sha256']for k,v in post['proofHashes'].items()}
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    hashes=json.loads(subprocess.check_output(ssh,input=catalog(seals['before.private.json']).encode(),timeout=30));assert len(hashes)==8
    env={'__file__':str(R/'pg657_native_counter.py'),'__name__':'current_normal_native_counter'}
    exec(compile(code(hashes,proof,seals),'<new normal cohort genuine eight sessions>','exec'),env);env['main']()


if __name__=='__main__':main()
