"""Independent full current/unused candidate post, actual resources gone; no authority."""
import inspect
from pyflakes.api import check
import pg2830_network_current_cold_post as prior
import pg1453_current_cold_post as runner
import pg2832_network_cold_unused_sources as s
from pg1082_cold_unused_candidate_post import CHECK
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2840-network-cold-unused-independent-post-v1'


def payload():
    raw=prior.payload()
    raw=raw.replace(prior.SLOT,SLOT).replace('PG2830-network-current-cold-independent-post-v1','PG2840-network-cold-unused-independent-post-v1')
    raw=raw.replace(s.current.PREPARED,s.SAVE).replace('finitePreparation=true','unusedCandidatePlacement=true')
    extra=s.one(CHECK,' import stat,grp\n',' import grp\n')
    for a,b in [('PG1068','PG2802'),('pg1068','pg2802'),('d5b00104280028d9ea81b44c1d1c805f3c2861ed',s.CANDIDATE),
        ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',s.DIGEST),
        ('5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b',s.SIGNATURE),
        ('pg1079-cold-candidate-v1',s.SAVE)]:extra=extra.replace(a,b)
    extra=s.one(extra," assert not any((pathlib.Path('/proc')/str(pid)).exists()for pid in (11678,11704))\n",'')
    extra=s.one(extra," assert first==env['snapshot']()and runtime==env['runtime_namespaces']()"," require(first==snapshot()and runtime==runtime_check())")
    raw=s.one(raw,'finally:\n errors=[]',extra+'finally:\n errors=[]')
    raw=s.one(raw,"'permissionIssued':False,","'permissionIssued':False,'candidateFull187Verified':True,'candidateNotActivated':True,'candidateSource':"+repr(s.CANDIDATE)+',')
    if check(raw,'<whole independent unused post>'):raise ValueError('whole current candidate post namespace required')
    compile(raw,'<independent actual unused post>','exec');return raw


def main():
    raw=inspect.getsource(runner.main).replace('pg1452-current-cold-owned-prepare-v1','pg2838-network-cold-unused-owned-place-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**runner.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<independent current candidate post dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
