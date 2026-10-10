"""Fixed observed disconnected DB is not evidence of old normal closure."""
import ast
import inspect
from pg1153_native_failed_owner_proof import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    s=previous().replace('native-failed-owner-proof-v1','native-failed-owner-proof-v2')
    start=s.index('def resource_zero():',s.index('JAVA=410279'))
    end=s.index('def current():',start)
    s=s[:start]+'''def resource_zero():
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0'])
'''+s[end:]
    ast.parse(s);return s


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1154-native-failed-owner-proof-v2').replace('PG1120-current-failed-capture-v1','PG1154-native-failed-owner-proof-v2')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<fixed disconnected owner proof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
