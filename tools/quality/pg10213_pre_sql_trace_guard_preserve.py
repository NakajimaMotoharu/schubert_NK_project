"""Preserve failed metadata guard before correction; no product operation."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

def main():
    invocation=capture(Path(__file__))
    out=data.BASE/'PG10213-pre-sql-trace-guard-preserved-v1'
    assert not out.exists()
    path=data.ROOT/'tools/quality/pg10214_pre_sql_trace.py'
    raw=path.read_bytes()
    assert b"assert logical[repository]['sha256']==prepared['allCurrentSourceInputHashes'][repository]" in raw
    verify(invocation)
    out.mkdir()
    (out/'original-failed-tool.py').write_bytes(raw)
    data.write(out/'manifest.json',dict(actualExit=0,invocation=invocation,originalGuardExit=1,
        originalToolSha256=data.sha(raw),failure='AssertionError at expected: historical logical SHA differs from current normal',
        source='d4ba0fcbe8855b9674413d395b46d2de7bb2ded9',manifestWrittenByOriginal=False,inventoryModifiedByOriginal=False,
        productTestsExecuted=0,bug='BUG-1805',ykt='YKT-1556',newAccepted=0,formalUpdated=False))
    print(data.sha((out/'manifest.json').read_bytes()))

if __name__=='__main__': main()
