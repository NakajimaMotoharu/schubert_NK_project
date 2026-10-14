"""Separate full candidate hostRO/receipt and untouched current/DB/durable post."""
import inspect
from pyflakes.api import check
import pg2840_network_cold_unused_post as prior
import pg1453_current_cold_post as runner
import pg2842_network_cold_ro_sources as s
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2850-network-cold-ro-independent-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace('PG2840-network-cold-unused-independent-post-v1','PG2850-network-cold-ro-independent-post-v1')
    raw=raw.replace(s.unused.SAVE,s.SAVE).replace('unusedCandidatePlacement=true','candidateImmutableVerified=true')
    addition=""" ro_flags=command(['findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG2802','--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
 require('ro'in ro_flags and 'rw'not in ro_flags)
"""
    raw=s.unused.one(raw,'finally:\n errors=[]',addition+'finally:\n errors=[]')
    raw=s.unused.one(raw,"'candidateFull187Verified':True,","'candidateFull187Verified':True,'candidateImmutableIndependentPost':True,")
    if check(raw,'<whole candidate RO independent post>'):raise ValueError('complete independent RO namespace required')
    compile(raw,'<actual independent candidate RO post>','exec');return raw


def main():
    raw=inspect.getsource(runner.main).replace('pg1452-current-cold-owned-prepare-v1','pg2848-network-cold-ro-owned-prepare-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**runner.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<independent full RO post dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
