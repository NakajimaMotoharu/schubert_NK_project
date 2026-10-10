"""Fresh current observer: cold admission window separate from actual Root budget."""
import ast
from pg1107_cold_current_observer import source as previous


def source():
    raw=previous().replace('pg1107','pg1112').replace('PG1107','PG1112')
    marker=".replace('cc9ed874-7f4f-450e-a188-8de1e42c8441','cbca8738-3b24-4090-b77c-bf029677cdd6')"
    if raw.count(marker)!=1:raise ValueError('fixed fresh observation window refused')
    old="deadline=min(deadline,int(m['ExecMainStartTimestampMonotonic'])/1e6+1860)"
    new="deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860"
    raw=raw.replace(marker,marker+'.replace('+repr(old)+','+repr(new)+')')
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1112 current ordinary observer>','exec'),{'__file__':__file__,'__name__':'__main__'})
