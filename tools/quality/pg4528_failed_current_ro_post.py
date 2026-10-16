"""Independent full current/candidate plus PID1 candidate-only RO and exact receipt."""
import ast
import inspect
import pg4520_failed_current_unused_post as previous

SLOT='pg4534-failed-current-ro-post-v1'


def normal_readonly_receipt(raw):
    expected=(b'genuineParentNormalWarningOriginal=false\ncurrentManagerGc=false\nfailedParent143DataOnly=true\ncandidateReadOnlyVerified=true\n'
      b'allNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloadsEpochWrites0=true\noldUnknownNormalized=false\n')
    if type(raw)is not bytes or raw!=expected:raise ValueError('exact new failed-data RO receipt required')
    return True


EXTRA=r'''
require(Path('/proc/self/ns/mnt').readlink()==Path('/proc/1/ns/mnt').readlink())
mount=subprocess.run(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG4432'],capture_output=True,text=True,timeout=10)
options=mount.stdout.strip().split(',');require(mount.returncode==0 and len(options)==len(set(options))and 'ro'in options and 'rw'not in options)
require(normal_readonly_receipt(Path('/var/lib/pgpt-s1-preservation/pg4526-failed-current-ro-completed-v2/complete.private').read_bytes()))
'''


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    marker=' candidate_first=candidate_verify();candidate_second=candidate_verify();require(candidate_first==candidate_second)\n'
    if raw.count(marker)!=1:raise ValueError('one full candidate verification inside tenRef scope')
    raw=raw.replace(marker,marker+''.join(' '+line+'\n'for line in EXTRA.strip().splitlines()),1)
    raw=inspect.getsource(normal_readonly_receipt)+'\n'+raw
    marker='value.update(candidate_first);'
    if raw.count(marker)!=1:raise ValueError('one final normal-close result')
    raw=raw.replace(marker,"value.update(candidateHostReadonlyVerified=True);"+marker,1)
    if previous.check(raw,'<complete failed-data RO post>'):raise ValueError('all emitted static0')
    ast.parse(raw);return raw


def main_source():
    raw=inspect.getsource(previous.main).replace('pg4516-place-v1.safe.json','pg4532-prepare-ro-v1.safe.json')
    return raw


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    exec(compile(main_source(),'<new independent RO completion observer>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
