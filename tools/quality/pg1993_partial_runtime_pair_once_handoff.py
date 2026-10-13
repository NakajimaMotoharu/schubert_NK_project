"""QA047 current pending-runtime pair once TERM; published file retained/no reload."""
import ast
import inspect
import pg1887_publication_pair_once_handoff as prior
from pg1991_fresh_runtime_partial_full_proof import payload as proof_payload,SLOT as PROOF_SLOT,Current
from pg1988_fresh_resume_retained_diagnosis import owner
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent,parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence
from pg1877_warning_publication_sources import once

SLOT='pg1993-partial-runtime-pair-once-handoff-v1'
PROOF_SHA='1dc3cb858cd5d6fa29a0cfcb74956832290b7791e5d5901df7569668eb6832af'


def payload():
    raw=proof_payload();raw=raw[:raw.index("tool=base/'pg1980-fresh-resume-tools-v1'")]
    raw=once(raw,'require(children == {498758})','require(children == (set()if REF_CLOSED else{498758}))')
    body=BODY.replace("expected['candidateNotPlaced']is True","expected['partialRuntimeFileVerified']is True and expected['reloadNotReserved']is True")
    body=body.replace('pg1664-current-unused-pair-proof-v1',PROOF_SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    body=once(body,"  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')","  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1846')")
    body=once(body,"  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())","  require(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846').is_dir()and(base/'pg1846-manifest.sig').is_file())")
    tree=prior.Typed().visit(ast.parse(body));tree=Current().visit(tree);ast.fix_missing_locations(tree);body=ast.unparse(tree)+'\n'
    body=body.replace("['29']","['31']").replace("['32']","['90']")
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nREF_CLOSED=False\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+body
    from pyflakes.api import check
    if check(raw,'<current partial runtime handoff>'):raise ValueError('all actual recovery globals required')
    compile(raw,'<one current partial runtime handoff>','exec');return raw


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA,'PROOF_SLOT':PROOF_SLOT,'payload':payload,'owner':owner}
    exec(compile(inspect.getsource(prior.main),'<current partial runtime queued handoff>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
