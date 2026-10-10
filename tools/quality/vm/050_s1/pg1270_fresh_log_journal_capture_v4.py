"""Current guarded Log oracle; all journal fields/order, distinct private raw reads."""
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1269_fresh_log_scoped_capture_v3 import payload as previous
import pg1131_journal_stable_projection as journal


def payload(seals):
    s=previous(seals).replace('pg1269-fresh-scoped-log-v3','pg1270-fresh-journal-log-v4').replace('PG1269-fresh-scoped-log-v3','PG1270-fresh-journal-log-v4')
    old='require(second.returncode == 0 and (not second.stderr) and (second.stdout == journal.stdout))'
    if s.count(old)!=1:raise ValueError('actual closed journal stability insertion required')
    s=s.replace(old,"journal_oracle=types.ModuleType('independent_allfield_journal');exec(JOURNAL_SOURCE,journal_oracle.__dict__);require(second.returncode==0 and not second.stderr and 0<len(second.stdout)<=16777216 and journal_oracle.project(second.stdout)==journal_oracle.project(journal.stdout))")
    marker="result.update(productionSource=data['source']['commit']"
    if s.count(marker)!=1:raise ValueError('actual scoped safe journal summary insertion required')
    s=s.replace(marker,"result.update(journalAllFieldEventOrderStable=True,requestJournalSecondSha256=hashlib.sha256(second.stdout).hexdigest(),requestJournalProjectionSha256=hashlib.sha256(journal_oracle.project(journal.stdout)).hexdigest())\n    "+marker)
    old="[('request-journal.private',journal.stdout),('result.safe.json',json.dumps(result,sort_keys=True).encode())]"
    if s.count(old)!=1:raise ValueError('actual private distinct raw preservation insertion required')
    s=s.replace(old,"[('request-journal.private',journal.stdout),('request-journal-second.private',second.stdout),('result.safe.json',json.dumps(result,sort_keys=True).encode())]")
    s='JOURNAL_SOURCE='+repr(inspect.getsource(journal))+'\n'+s
    compile(s,'<complete fixed same-source Log v4>', 'exec');return s


def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1270-fresh-journal-log-v4')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only current guarded Log v4>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
