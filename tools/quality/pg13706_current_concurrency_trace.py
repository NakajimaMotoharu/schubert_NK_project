"""Five existing Main reason refs only; preserve original WBS and all995 historical runtime rows."""
import f03_current_concurrency_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not trace.OUT.exists() and (trace.data.ROOT/trace.RECORD).is_file()
    prior, rows, raw, snap = trace.inputs()
    assert (trace.data.ROOT/trace.INV).read_bytes() == raw and (trace.data.ROOT/trace.SNAP).read_bytes() == snap
    value = trace.expected(prior, rows)
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    value.update(invocation=invocation, wholeWbsAuditBefore=observed)
    verify(invocation)
    trace.OUT.mkdir()
    trace.data.write(trace.OUT/'manifest.json', value)
    print(trace.data.sha((trace.OUT/'manifest.json').read_bytes()))
