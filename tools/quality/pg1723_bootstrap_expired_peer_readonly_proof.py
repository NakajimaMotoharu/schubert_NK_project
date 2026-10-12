"""BUG1156 constructor-before-monitor failure: current server peer is gone.

The old 1722 requirement for a live peer failed (signals0), not passed. Fresh
SQL proves server owner/advisory zero; full retained Java/FD/M-A remain owned.
No close success is inferred from server idle timeout.
"""
import inspect
import pg1722_bootstrap_db_owner_readonly_proof as prior

SLOT='pg1723-bootstrap-expired-peer-proof-v1'
PEER=r'''
def same_peer():
 q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
 sockets={os.readlink(f)[8:-1]for f in(P/'fd').iterdir()if os.readlink(f).startswith('socket:[')}
 rows=[l.split()for n in ['tcp','tcp6']for l in pathlib.Path('/proc/net',n).read_text().splitlines()[1:]]
 require(not any(len(r)>=10 and r[3]=='01'and r[9]in sockets and r[2].endswith(':1538')for r in rows))
 return {'serverPeers':0,'advisory':0,'ownedJavaEstablishedDatabaseSocket0':True,'oldCloseUnknown':True}
'''

def payload():
    raw=prior.payload()
    start=raw.index('def same_peer():');end=raw.index('bus=dbus.SystemBus(private=True);manager=',start)
    raw=raw[:start]+PEER+'\n'+raw[end:]
    raw=raw.replace("lines[-2:]==[b'1',b'1']","lines[-2:]==[b'0',b'0']")
    raw=raw.replace(prior.SLOT,SLOT).replace("'backendPid':peer['activity']['pid']", "'backendPid':None").replace("'samePeer':True", "'serverPeerAdvisory0':True")
    raw=raw.replace("'noRefChildOrUnitStart':True", "'noRefChildOrUnitStart':True,'serverPeerAdvisory0':True")
    from pyflakes.api import check
    if check(raw,'<retainedJava current server0 proof>'):raise ValueError('generated static refused')
    compile(raw,'<retainedJava current server0 proof>','exec');return raw

def main():
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<new expired-peer full proof transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
