"""Current failed Java with expired DB peer: never infer old normal close."""
import pg1351_bootstrap_failed_owner_proof_v2 as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw = previous.payload(seals)
    start = raw.index(' q="select json_build_object(')
    end = raw.index('\n links=[];sockets=set()', start)
    raw = raw[:start] + '''
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0'])
''' + raw[end:]
    start = raw.index(' local={')
    end = raw.index('\n locks={}', start)
    raw = raw[:start] + '''
 remote={'0100007F:1538','0000000000000000FFFF00000100007F:1538'}
 network=[line.split()for name in ['tcp','tcp6']for line in(p/'net'/name).read_text().splitlines()[1:]]
 require(not any(len(r)>=10 and r[2]in remote and r[3]=='01'and r[9]in sockets for r in network))
''' + raw[end:]
    raw = raw.replace("'backend':peer['pid'],'clientPort':peer['clientPort']", "'backend':None,'clientPort':None,'expiredDbPeerGone':True")
    raw = raw.replace("lines[-2:]==[b'1',b'1']", "lines[-2:]==[b'0',b'0']")
    raw = raw.replace('pg1351-bootstrap-failed-owner-v2', 'pg1352-bootstrap-expired-peer-v1').replace('PG1351-bootstrap-failed-owner-v2', 'PG1352-bootstrap-expired-peer-v1')
    compile(raw, '<actual expired peer zero proof>', 'exec')
    return raw

def source():
    return previous.source().replace('pg1351-bootstrap-failed-owner-v2', 'pg1352-bootstrap-expired-peer-v1')

def main():
    env = dict(previous.prior.prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<expired peer fresh proof>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
