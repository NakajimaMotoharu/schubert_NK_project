"""Update20 current Test hashes only; preserve all995 owners/costs/old runtime and unknown two."""
import pg13462_residual_literal_config as cfg
import f03_literal_batch_trace_v2 as core

SOURCE = '05e6589b78e6fabe043e5a3c75d1e39494da83e3'
NORMAL = '9b1070efc57add00d537788d6f44af0c73f526a9e6d3048e079c2830af5b2f56'
PROOF = 'aeb8fb9866da13e9586db35efcae88b37a1eabe3dcd1c5a7f5cee6db55dc0557'

def state_after():
    return core.state_after(cfg)

if __name__ == '__main__':
    core.main(cfg,SOURCE,NORMAL,PROOF)
