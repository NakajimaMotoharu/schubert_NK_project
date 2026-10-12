"""SSC271 proved same runtime holders: Ref then Java once TERM, finite reap."""
import inspect
import pg1521_profile_pair_once_handoff as prior
import pg1564_runtime_retained_pair_proof as proof

SLOT='pg1565-retained-runtime-pair-handoff-v1'
PROOF_SHA='c1f366c09f924af5afc6a628ee2ca0a030823be7c385ee0738ca55d5da8ac911'

def payload():
    raw=inspect.getsource(prior.payload).replace('PG269-original-io-profile','PG271-runtime-once')
    ns={**prior.__dict__,'proof':proof,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA}
    exec(compile(raw,'<SSC271 once owned runtime pair handoff>','exec'),ns);return ns['payload']()

def main():
    fixed=prior.json.loads((prior.W/proof.SLOT/'manifest.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual complete current pair proof required')
    ns={**prior.__dict__,'proof':proof,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<new once owned runtime transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
