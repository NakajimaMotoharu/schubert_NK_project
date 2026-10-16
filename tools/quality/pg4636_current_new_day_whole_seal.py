"""Bind new-day independent SQL oracle; preserve genuine guard and save raw before checks."""
import ast
import inspect
from pyflakes.api import check
import pg4632_current_new_day_rows_oracle as rows
from pg2814_network_newboot_readonly import one
from pg4442_failed_current_view_qualification import strict_equal


def patch(raw,binding):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one whole independent SQL oracle')
    old=ast.get_source_segment(raw,nodes[0])
    independent=rows.source()+"\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_current(old,new,"+repr(binding['run'])+",cutoff,upper)\n"
    result=one(raw,old,'ORACLE='+repr(independent))
    marker="SAVE=BASE/'pg4636-current-whole-seal-v1';require(not os.path.lexists(SAVE))"
    setup=r'''
RAW_SAVE=BASE/'pg4636-current-whole-seal-v1-raw';require(not os.path.lexists(RAW_SAVE));os.umask(0o077);RAW_SAVE.mkdir(mode=0o700)
def preserve_raw(label,blob):
 require(type(label)is str and re.fullmatch('[a-z0-9-]+',label)is not None and type(blob)is bytes)
 with(RAW_SAVE/(label+'.private')).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
 fd=os.open(RAW_SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
'''
    result=one(result,marker,marker+'\n'+inspect.getsource(strict_equal)+'\n'+setup)
    old=" for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],67108864).splitlines():"
    new=" sql_raw=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],67108864)\n preserve_raw('sql-'+str(time.monotonic_ns()),sql_raw)\n for line in sql_raw.splitlines():"
    result=one(result,old,new)
    marker=" business=types.ModuleType('independent_sql');"
    result=one(result,marker," preserve_raw('captured-'+str(time.monotonic_ns()),json.dumps({'units':us,'actors':actors,'configuration':configuration,'rows':rs,'pid1':proof.rows,'doneSha256':hashlib.sha256(proof.done).hexdigest()},sort_keys=True).encode())\n"+marker)
    marker=' current=capture();require(current==capture());SAVE.mkdir(mode=0o700)'
    new=" current=capture();preserve_raw('complete-first',json.dumps(current,sort_keys=True).encode())\n second=capture();preserve_raw('complete-second',json.dumps(second,sort_keys=True).encode());require(strict_equal(current,second));SAVE.mkdir(mode=0o700)"
    result=one(result,marker,new)
    result=one(result,' require(current==capture())'," final=capture();preserve_raw('complete-final',json.dumps(final,sort_keys=True).encode());require(strict_equal(current,final))")
    # Only the SQL oracle may change. The genuine terminal/source guard is exact.
    def guard(value):
        return next(ast.literal_eval(n.value)for n in ast.parse(value).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GUARD'for t in n.targets))
    if guard(raw)!=guard(result):raise ValueError('genuine guard must remain exact')
    if check(result,'<new day whole seal all raw before compare>'):raise ValueError('complete emitted static0')
    return result
