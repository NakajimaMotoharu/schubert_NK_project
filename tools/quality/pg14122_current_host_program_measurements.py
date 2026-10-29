"""Record scoped independent program measurements without recomputing Product results."""
import current_host_program_measurements_v1 as registry
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit

if __name__=='__main__':
    invocation=capture(__file__)
    assert not registry.OUT.exists() and (registry.data.ROOT/registry.RECORD).is_file()
    prior,refs,programs,natural,raw,snap,pin,modules=registry.inputs()
    assert (registry.data.ROOT/registry.INV).read_bytes()==raw and (registry.data.ROOT/registry.SNAP).read_bytes()==snap
    value=registry.expected(prior,refs,programs,natural,pin,modules)
    observed=audit();assert observed['actualExit']==1 and not observed['passed']
    value.update(invocation=invocation,wholeWbsAuditBefore=observed)
    verify(invocation);registry.OUT.mkdir();registry.data.write(registry.OUT/'manifest.json',value)
    print(registry.data.sha((registry.OUT/'manifest.json').read_bytes()))
