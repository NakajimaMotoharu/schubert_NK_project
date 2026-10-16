"""SSC297 pure exact pre-operation pair predicates; no operation capability."""
JAVA=(827198,16494387,'72e6609effcd0397c9a679d8bea26588975bd6eaf56cff535e4c4b954bd6a601')
PYTHON=(827230,16494598,'8c039420d33e9ba1c67afaabf06bf878f0333ee262d87bc3b77f7c608dee588c')
JAVA_FDS={str(n)for n in range(97)}|{'99','100','101','128'}
PYTHON_FDS={'0','1','2','3'}
CGROUP='0::/user.slice/user-1000.slice/session-1025.scope\n'


def require(value):
    if value is not True:raise ValueError('exact pre-operation retained pair refused')


def stable(label,old,now,java_gone=False):
    require(label in ['java','python']and type(old)is dict and type(now)is dict and type(java_gone)is bool)
    identity=JAVA if label=='java'else PYTHON
    for v in [old,now]:
        require((v.get('pid'),v.get('ticks'),v.get('argvSha256'))==identity and v.get('cgroup')==CGROUP)
        a=v.get('authority');require(type(a)is dict)
        require(a.get('Uid','').split()==['0']*4 and a.get('Gid','').split()==['0']*4 and a.get('Groups','').split()==['0'])
        require(a.get('NoNewPrivs')=='0'and a.get('CapInh')==a.get('CapAmb')=='0000000000000000'
            and a.get('CapPrm')==a.get('CapEff')==a.get('CapBnd')=='000001ffffffffff')
        require(v.get('children')==([827230]if label=='java'else[]))
        require(type(v.get('fds'))is dict and set(v['fds'])==(JAVA_FDS if label=='java'else PYTHON_FDS))
    expected={**old,'authority':dict(old['authority'])}
    if label=='python'and java_gone:expected['authority']['PPid']='1'
    require(old['authority']['PPid']==('827196'if label=='java'else'827198'))
    # Every descriptor target, inode/type/ownership/size/timestamp/fdinfo and
    # every authority field are exact. No filtering or count-only acceptance.
    require(now==expected)
    return True


def peers(reference,current,java_gone=False):
    require(type(reference)is dict and type(current)is dict and type(java_gone)is bool)
    for key in ['units','actors','durable','native','startup','runtime']:
        require(current.get(key)==reference.get(key))
    require(current['database']['rows']==reference['database']['rows'])
    if java_gone:
        require(current['database']['peers']==[]and current['database']['locks']==[]and current['flocks']==[])
    else:
        before=reference['database']['peers'];after=current['database']['peers']
        require(len(before)==len(after)==1 and before[0]['pid']==after[0]['pid']==827228)
        require(after[0]['state']in ['active','idle in transaction'])
        require({k:v for k,v in before[0].items()if k!='state'}=={k:v for k,v in after[0].items()if k!='state'})
        require(current['database']['locks']==reference['database']['locks']and len(current['database']['locks'])==1)
        def locks(rows):
            require(len(rows)==2)
            parts=[line.split()[1:]for line in rows]
            require(all(p[:4]==['FLOCK','ADVISORY','WRITE','827198']for p in parts))
            return sorted(parts)
        require(locks(current['flocks'])==locks(reference['flocks']))
    return True


def tcp_rows(text):
    require(type(text)is str)
    rows=[]
    for line in text.splitlines()[1:]:
        fields=line.split();require(len(fields)>=10)
        rows.append(fields)
    return rows


def database_socket(pair):
    require(type(pair)is dict)
    client=pair['java']['fds']['96']['target'];require(client=='socket:[14177460]')
    server=[f['target']for f in pair['backend']['fds'].values()if f['target'].startswith('socket:')]
    require(server==['socket:[14176496]'])
    rows=tcp_rows(pair['tcp'])+tcp_rows(pair['tcp6'])
    a=[r for r in rows if r[9]=='14177460'];b=[r for r in rows if r[9]=='14176496']
    require(len(a)==len(b)==1 and a[0][3]==b[0][3]=='01')
    require(a[0][1:3]==['0000000000000000FFFF00000100007F:9AA0','0000000000000000FFFF00000100007F:1538'])
    require(b[0][1:3]==['0100007F:1538','0100007F:9AA0'])
    return True
