"""Separate current canonical runtime/original/resource post, no signal or replay."""
import inspect
import pg1522_profile_pair_independent_closing as prior
import pg1564_runtime_retained_pair_proof as proof
from pg1565_runtime_pair_handoff import SLOT as HANDOFF,PROOF_SHA

SLOT='pg1566-retained-runtime-pair-closing-v1'

def payload():
    raw=inspect.getsource(prior.payload).replace("marker=\"{'98426.term-once.private','98452.term-once.private'}\"", "marker=\"{'105206.term-once.private','105232.term-once.private'}\"")
    raw=raw.replace("{'98426.term-once.private','98452.term-once.private','after.private.json','complete.private'}", "{'105206.term-once.private','105232.term-once.private','after.private.json','complete.private'}")
    ns={**prior.__dict__,'proof':proof,'HANDOFF':HANDOFF,'PROOF_SHA':PROOF_SHA,'SLOT':SLOT}
    exec(compile(raw,'<separate owned runtime resource closing>','exec'),ns);return ns['payload']()

def main():
    ns={**prior.__dict__,'proof':proof,'HANDOFF':HANDOFF,'PROOF_SHA':PROOF_SHA,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<new only independent runtime post>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
