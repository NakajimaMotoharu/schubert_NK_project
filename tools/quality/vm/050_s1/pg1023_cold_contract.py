"""Pure owned-cold kernel/DB observation contract; no acquisition or mutation authority."""
import os
import stat

def owned_flocks(lines,metadata,parent):
    if type(lines)is not list or any(type(x)is not str for x in lines):raise ValueError('lock lines refused')
    if type(parent)is not int or parent<=1 or type(metadata)is not dict or set(metadata)!= {'maintenance.lock','startup-admission.lock'}:raise ValueError('lock owner refused')
    identities={}
    for name,m in metadata.items():
        if type(m)is not list or len(m)!=9 or any(type(x)is not int for x in m)or m[2:7]!=[0,0,stat.S_IFREG|0o600,1,0]:raise ValueError('lock metadata refused')
        key=(os.major(m[0]),os.minor(m[0]),m[1])
        if key in identities:raise ValueError('lock identity refused')
        identities[key]=name
    counts={name:0 for name in metadata}
    for line in lines:
        f=line.split();blocked=len(f)>1 and f[1]=='->'
        if blocked:f=[f[0],*f[2:]]
        if len(f)<2 or f[1]!='FLOCK':continue
        if len(f)!=8:raise ValueError('lock record refused')
        try:
            parts=f[5].split(':')
            if len(parts)!=3:raise ValueError('lock address refused')
            key=(int(parts[0],16),int(parts[1],16),int(parts[2]))
        except ValueError:raise ValueError('lock address refused')from None
        if key not in identities:continue
        if blocked or f[2:4]!=['ADVISORY','WRITE']or f[4]!=str(parent)or f[6:]!=['0','EOF']:raise ValueError('lock ownership refused')
        counts[identities[key]]+=1
    if set(counts.values())!={1}:raise ValueError('lock cardinality refused')
    return counts

def owned_peer_sql(backend):
    if type(backend)is not int or not 0<=backend<2147483647 or backend==1:raise ValueError('backend refused')
    roles="usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector')"
    # The authenticated parent verifies actual transaction_read_only through its
    # same connection before/through/after the observation. A heartbeat may be active.
    tag="usename='schubert_batch'and application_name='PG243-cold-empty'and backend_type='client backend'and state in('idle in transaction','active')"
    return ("select count(*)from pg_stat_activity where datname='schubert_nk'and "+roles+"and pid<>"+str(backend)+";"
      "select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted and pid<>"+str(backend)+";"
      "select count(*)from pg_stat_activity a where datname='schubert_nk'and pid="+str(backend)+" and "+tag+
      "and exists(select 1 from pg_locks l where l.pid=a.pid and locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock'and granted);")
