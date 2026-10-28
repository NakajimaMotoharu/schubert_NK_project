"""Current single Test SHA/limited measured qualification; original ownership and runtime retained."""
import g07_host_class_provenance_inputs as data
import f03_lgs_boundary_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

PROOF = ('PG13586-lgs-boundary-whole-eight-measured-post-v1', '47aaada6cebdb482f4f12dcd69fe3b92fd5eed22a78c8357f302a8cf09304c65')

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not trace.OUT.exists() and (data.ROOT/trace.cfg.RECORD).is_file()
    prior, hashes, raw, snap = trace.inputs()
    assert (data.ROOT/trace.INV).read_bytes() == raw and (data.ROOT/trace.SNAP).read_bytes() == snap
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json', PROOF[1])
    value = trace.expected(prior, hashes, proof, PROOF[1])
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    value.update(invocation=invocation, wholeWbsAuditBefore=observed)
    verify(invocation)
    trace.OUT.mkdir()
    data.write(trace.OUT/'manifest.json', value)
    print(data.sha((trace.OUT/'manifest.json').read_bytes()))
