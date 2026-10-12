"""SSC281: approved pool ceilings, fixed sole management peer, no extra role."""


def validate_current_peers(rows,lock_count,backend):
    if type(rows)is not list or type(lock_count)is not int or lock_count!=1 or type(backend)is not int or backend<=1:raise ValueError('typed sole management ownership required')
    bounds={'schubert_app':(2,8),'schubert_web_session':(1,2),'schubert_batch':(1,1)}
    apps={'schubert_app':'schubert-nk-api','schubert_web_session':'schubert-nk-web','schubert_batch':'PG998-native-stop'}
    pids=[];ports=[]
    for row in rows:
        if type(row)is not dict or row.get('role')not in bounds:raise ValueError('known owned role required')
        role=row['role']
        if type(row.get('pid'))is not int or row['pid']<=1 or type(row.get('port'))is not int or not 1<=row['port']<=65535 or row.get('address')!='127.0.0.1'or row.get('database')!='schubert_nk'or type(row.get('backendStart'))is not str or not row['backendStart']or row.get('app')!=apps[role]:raise ValueError('typed same service loopback peer required')
        pids.append(row['pid']);ports.append(row['port'])
    if len(set(pids))!=len(pids)or len(set(ports))!=len(ports):raise ValueError('unique backend and client port required')
    for role,(minimum,maximum)in bounds.items():
        count=sum(row['role']==role for row in rows)
        if not minimum<=count<=maximum:raise ValueError('approved pool bounds required')
    batch=next(row for row in rows if row['role']=='schubert_batch')
    if batch['pid']!=backend or batch.get('state')!='idle in transaction':raise ValueError('fixed retained management generation required')
    return batch
