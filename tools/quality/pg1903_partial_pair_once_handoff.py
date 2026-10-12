"""One current partial pair handoff; approved public/Unit state never rolled back."""
import ast
import inspect
import pg1887_publication_pair_once_handoff as prior
from pg1902_partial_publication_pair_proof import payload as proof_payload,SLOT as PROOF_SLOT,Current
from pg1898_partial_publication_diagnosis import owner
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent,parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence
from pg1877_warning_publication_sources import once

SLOT='pg1903-partial-pair-once-handoff-v1'
PROOF_SHA='1ccaea9fbec075251f656f79f5b72edebd93a2ed5a9aeb97f8551a90b6ebe9ed'


def payload():
    raw=proof_payload();raw=raw[:raw.index('a=pair();require(a==pair());locks=')]
    raw=once(raw,'require(children == {493146})','require(children == (set()if REF_CLOSED else{493146}))')
    body=BODY.replace("expected['candidateNotPlaced']is True","expected['partialPublicationQualified']is True and expected['reloadNotReserved']is True")
    body=body.replace('pg1664-current-unused-pair-proof-v1',PROOF_SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    body=once(body,"  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')","  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1846')")
    body=once(body,"  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())","  require(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846').is_dir()and(base/'pg1846-manifest.sig').is_file())")
    # The historical body was literal291213/291242, so first bind its own actual
    # role constants, then the new current pair; never replace arbitrary digits.
    tree=prior.Typed().visit(ast.parse(body));tree=Current().visit(tree);ast.fix_missing_locations(tree);body=ast.unparse(tree)+'\n'
    body=body.replace("['29']","['31']").replace("['32']","['90']")
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'").replace("len(old['fds']) != 101","len(old['fds']) != 102")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nREF_CLOSED=False\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+body
    from pyflakes.api import check
    if check(raw,'<current partial handoff whole namespace>'):raise ValueError('all actual partial handoff globals required')
    compile(raw,'<one current partial pair handoff>','exec');return raw


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA,'PROOF_SLOT':PROOF_SLOT,'payload':payload,'owner':owner}
    exec(compile(inspect.getsource(prior.main),'<current partial same gate handoff>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
