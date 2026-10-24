"""BUG1702 new-only metadata closure, old javap/failed tool preserved; no product replay."""
import hashlib
import json
import subprocess
import pg8412_web_scrape_six_trace as trace

if __name__ == '__main__':
    old = trace.host.W / 'pg8412-web-scrape-six-trace-v1'
    text = (old / 'policy-fields.stdout.log').read_text()
    receipt = json.loads((old / 'policy-fields-exit.safe.json').read_text())
    assert receipt['actualExit'] == 0 and trace.host.sha(old / 'policy-fields.stdout.log') == receipt['stdoutSha256']
    assert len([line for line in text.splitlines() if line.strip().endswith(';') and '(' not in line]) == 6
    fields, methods = trace.field_contract.verify_contract(text, trace.FIELDS)
    negatives = trace.field_contract.negative_guards(text, trace.FIELDS)
    assert len(fields) == 3 and len(methods) == 2 and len(negatives) == 5
    original = subprocess.check_output(['git', 'show', 'd3cbe2526c045b398f257d38260f3ae6d3da6f33:tools/quality/pg8412_web_scrape_six_trace.py'], cwd=trace.host.ROOT)
    assert b"len(field_lines) == len(parsed) == len(fields) == 3" in original
    trace.SLOT = trace.host.W / 'pg8413-web-scrape-fixed-trace-v1'
    trace.OUT = trace.host.BASE / 'PG8413-web-scrape-fixed-trace-v1'
    trace.main()
    print(json.dumps(dict(bug='BUG-1702', originalFailedToolGitRef='d3cbe2526c045b398f257d38260f3ae6d3da6f33:tools/quality/pg8412_web_scrape_six_trace.py', originalToolSha256=hashlib.sha256(original).hexdigest(), originalFieldStdoutSha256=receipt['stdoutSha256'], oldReaderCount=6, actualFields=len(fields), actualMethods=len(methods), grammarNegatives=negatives, productTestsReplayed=0)))
