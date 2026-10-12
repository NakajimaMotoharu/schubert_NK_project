"""Separate candidate hostRO/normal owner/current closing; no remount or placement."""
import inspect
import pg1545_pending_unused_independent_closing as prior

EXTRA=r'''
ro=BASE/'pg1549-pending-candidate-host-ro-v1';raw=(ro/'after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='aacf474aa20bb81775b974f37c9eb8415115088cb4b992022587115cf9a17874')
ro_after=json.loads(raw);require(ro_after['candidateOnlyHostRo']is True and ro_after['currentApprovalEpochDbUnitsPreserved']is True)
require(ro_after['parent']['pid']==102679 and ro_after['parent']['ticks']==2660239 and ro_after['parent']['argvSha256']=='ff9777246792d16ec5bb67e695076bbdd0afda3eaf2da961aacfe283ddcb7092'and not pathlib.Path('/proc/102679').exists())
require((ro/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\ncandidateHostRo=true\nepochDbBusinessWrites=0\n')
require(hashlib.sha256(json.dumps(ro_after['current'],sort_keys=True).encode()).hexdigest()=='7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5')
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),ro_after['parent']['locks']))
for name,m in ro_after['parent']['locks'].items():require(metadata(ROOT/name)==m)
flags=command(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG1544'],4096).decode('ascii').strip().split(',')
require(len(flags)==len(set(flags))and 'ro'in flags and 'rw'not in flags)
'''

def payload():
    s=prior.payload().replace("POST=BASE/'pg1545-pending-unused-independent-closing-v1'","POST=BASE/'pg1550-pending-candidate-ro-independent-closing-v1'")
    marker="placement=BASE/'pg1539-pending-unused-placement-v1'"
    if s.count(marker)!=1:raise ValueError('fixed readonly closing boundary refused')
    s=s.replace(marker,EXTRA+'\n'+marker).replace("'unusedCandidateSigned187Qualified':unused_candidate_normal", "'candidateHostRoQualified':True,'candidateRoOwnerPeerAndLocksGone':True,'unusedCandidateSigned187Qualified':unused_candidate_normal")
    compile(s,'<readonly host immutable candidate/current closing>','exec');return s

def main():
    s=inspect.getsource(prior.prior.previous.main).replace('pg1508-publication-recovery-closing-v3','pg1550-pending-candidate-ro-independent-closing-v1')
    ns={**prior.prior.previous.__dict__,'payload':payload};exec(compile(s,'<new readonly candidate RO closing transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
