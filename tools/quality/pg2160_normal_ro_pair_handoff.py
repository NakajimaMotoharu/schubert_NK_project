"""Current proved no-bus RO child then Java ordinary once TERM, queued gate."""
import ast
import inspect
import types
import pg2140_current_normal_pair_handoff as prior
from pg2158_normal_ro_retained_pair_proof import payload as proof_payload,SLOT as PROOF_SLOT,Current
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent,parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT='pg2160-normal-ro-pair-owned-handoff-v1'
PROOF_SHA='670565f7e39578818f98213e7b9712e0a05a7a38c66f79561e13d921983d4e83'


def owner():
    raw=inspect.getsource(prior.owner)
    for old,new in [('388894','398057'),('12454900','12647485'),('2c1d5dd068a3f01aad439bd64913558e85717650d413372182c35003be36d318','8ef30749951a8857914ae9fa434b88977476e15356ca194bdc75253cd9b54908')]:raw=raw.replace(old,new)
    ns=dict(prior.__dict__);exec(compile(raw,'<actual current RO host owner>','exec'),ns);return ns['owner']()


def payload():
    raw=proof_payload();raw=raw[:raw.index("tool = base / 'pg2152-normal-candidate-ro-tools-v1'")]
    raw=raw.replace('require(children == {680289})','require(children == (set()if REF_CLOSED else{680289}))')
    body=BODY.replace('pg1664-current-unused-pair-proof-v1',PROOF_SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    body=body.replace("expected['candidateNotPlaced']is True","expected['candidatePlacedUnchanged']is True")
    body=body.replace('0.1.0-PG1544','0.1.0-PG1846')
    body=body.replace("not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists()","pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').is_dir()and(base/'pg2126-manifest.sig').is_file()")
    # First bind the approved algorithm's historical identity, then the new cohort.
    tree=prior.proof.Current().visit(ast.parse(body));tree=Current().visit(tree);ast.fix_missing_locations(tree)
    body=ast.unparse(tree).replace("['29']","['31']").replace("['32']","['90']")+'\n'
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nREF_CLOSED=False\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+body
    from pyflakes.api import check
    if check(raw,'<actual no-bus RO once handoff>'):raise ValueError('whole actual namespace required')
    compile(raw,'<actual no-bus RO once handoff>','exec');return raw


def main():
    fixed='fe46d194a8171cf59fb37ad234226e82e0fec748'
    # The old main's guard is fixed to this current immutable operation, no HEAD change.
    raw=inspect.getsource(prior.main).replace('7e519fe34b07beef24a3d943fddba639299842ed',fixed)
    ns={**prior.__dict__,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA,'payload':payload,'owner':owner,'proof':types.SimpleNamespace(SLOT=PROOF_SLOT)}
    exec(compile(raw,'<current RO queued recovery entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
