"""Whole-field stable PID1 receipt, raw journal reads privately retained."""
import ast
import inspect
from pg1193_completed_resume_receipt import payload as previous
import pg1131_journal_stable_projection as journal
import pg1117_current_done_probe as transport


def payload():
    s=previous();nodes=[n for n in ast.parse(inspect.getsource(journal)).body if isinstance(n,ast.FunctionDef)]
    if {n.name for n in nodes}!={'pairs','project'}:raise ValueError('fixed complete pure journal source required')
    s=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+s
    s=s.replace("rows=[json.loads(x)for x in raw.splitlines()]", "rows=json.loads(project(raw))")
    marker='if show()!=state or os.path.lexists(base/\'active\')'
    if s.count(marker)!=1:raise ValueError('fixed complete receipt stability insertion refused')
    s=s.replace(marker,'again=subprocess.check_output(cmd,timeout=10)\n'+marker)
    s=s.replace('subprocess.check_output(cmd,timeout=10)!=raw', 'project(again)!=project(raw)')
    i=s.index("print(json.dumps({'receipt':result")
    s=s[:i]+SAVE+s[i:]
    s=s.replace("'rawPrinted':False", "'rawPrinted':False,'privateProofHashes':proofs,'privateRawJournalReadsPreserved':True")
    ast.parse(s);return s


SAVE=r'''
private=Path('/var/lib/pgpt-s1-preservation/pg1194-completed-resume-receipt-v2')
if os.path.lexists(private)or os.geteuid()!=0:raise ValueError('new private receipt namespace required')
os.umask(0o077);private.mkdir(mode=0o700);proofs={}
for name,data in [('journal-first.private.jsonl',raw),('journal-second.private.jsonl',again),('run.private',anchor),('begin.private',begin),('done.private',done),('receipt.private.json',json.dumps({'binding':BINDING,'current':state,'result':result,'currentStateClass':currentStateClass},sort_keys=True).encode())]:
 with(private/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 proofs[name]=hashlib.sha256(data).hexdigest()
fd=os.open(private,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1183-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1194-completed-resume-receipt-v2').replace('PG1117-current-done-receipt-v1','PG1194-completed-resume-receipt-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(s,'<whole-value new PID1 receipt>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
