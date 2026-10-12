"""New-only BUG1163 fix; PID1 raw field order is not a completion claim."""
import inspect
import ast
import pg1764_warning_terminal_capture as prior
from pg1762_next_day_done_receipt import payload as old_receipt


def projection_source():
    raw=old_receipt()
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name in {'pairs','project'}]
    if {n.name for n in nodes}!={'pairs','project'}:raise ValueError('two fixed independent projection definitions required')
    return '\n'.join(ast.get_source_segment(raw,n)for n in nodes)+'\n'


def payload():
    raw=prior.payload()
    raw=projection_source()+raw
    old="require({n:show(n)for n in names}==units and read(donepath)==done and subprocess.check_output(cmd,timeout=10)==journal)"
    if raw.count(old)!=1:raise ValueError('one journal boundary required')
    raw=raw.replace(old,"again=subprocess.check_output(cmd,timeout=10)\nrequire({n:show(n)for n in names}==units and read(donepath)==done and project(again)==project(journal))")
    raw=raw.replace("('pid1.private.jsonl',journal)","('pid1-first.private.jsonl',journal),('pid1-second.private.jsonl',again)")
    raw=raw.replace('pg1764-warning-terminal-capture-v1','pg1765-warning-terminal-capture-v2')
    compile(raw,'<strict warning journal capture>','exec')
    return raw


def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'payload':payload,'SLOT':'pg1765-warning-terminal-capture-v2'}
    exec(compile(raw,'<new-only warning transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
