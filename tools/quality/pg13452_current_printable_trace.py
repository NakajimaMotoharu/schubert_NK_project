"""Update only34 current hashes; retain all995 canonical owner/cost/old runtime and unknown two."""
import pg13440_current_printable_literal_config as cfg
import f03_literal_batch_trace_v2 as core

SOURCE = '99fa8e93a67184377012d90cb41fdbc11a86cfad'
NORMAL = '06c38882aaace8836626a112de79083a89ae2a374db1df6c565c16fbe2f99cb8'
PROOF = '159757104dbc39e5e36b953f9a84c63718716f7f43e51bb21027138fd351c980'

def state_after():
    return core.state_after(cfg)

if __name__ == '__main__':
    core.main(cfg,SOURCE,NORMAL,PROOF)
