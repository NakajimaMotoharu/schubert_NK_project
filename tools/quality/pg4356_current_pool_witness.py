"""Fresh socket/peer witness after BUG1350; no historical TCP ownership fabrication."""
import inspect
import pg4354_current_reference_delta as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4356-current-pool-witness-v1'


def payload():
    raw = once(previous.payload(), "save=base/'" + previous.SLOT + "'", "save=base/'" + SLOT + "'")
    marker = "sha_private=save_private('observed.private.json',private)"
    body = """table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]
roles={'schubert_app':('schubert-nk-api.service','schubert-nk-api'),'schubert_web_session':('schubert-nk-web.service','schubert-nk-web')}
witnesses={};safe={}
for peer in samples[-1]['database']['peers']:
 require(peer['user']in roles);unit,application=roles[peer['user']]
 require(peer['address']=='127.0.0.1'and peer['application']==application)
 actor=samples[-1]['actors'][unit];tcp_pair(table,peer['port'],inodes(actor['pid']),inodes(peer['pid']))
 matches=[r for r in table if endpoint(r[1])==('127.0.0.1',peer['port'])and endpoint(r[2])==('127.0.0.1',5432)and r[3]=='01'and r[9]in inodes(actor['pid'])]
 require(len(matches)==1)
 fdmap=samples[-1]['detailedActors'][unit]['fds'];fds=[n for n,v in fdmap.items()if v['target']=='socket:['+matches[0][9]+']'];require(len(fds)==1)
 witnesses.setdefault(unit,{})[fds[0]]={'peer':peer,'client':matches[0]}
 safe.setdefault(unit,{})[fds[0]]={'flags':fdmap[fds[0]]['flags'],'mountId':fdmap[fds[0]]['mountId'],'socketUidGid':fdmap[fds[0]]['metadata'][2:4],'socketMode':fdmap[fds[0]]['metadata'][4]}
private['ordinaryDatabaseFds']=witnesses;private['tcpTable']=table
"""
    raw = once(raw, marker, body + marker)
    return once(raw, "'referenceDeltaPaths':reference_delta", "'currentPoolFdWitnesses':safe,'referenceDeltaPaths':reference_delta")


def main():
    ns = {**vars(previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<fresh socket read transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
