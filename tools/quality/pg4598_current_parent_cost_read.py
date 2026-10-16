"""Bounded kernel counters of the already-bound Root only; no signals/jcmd or renewal."""
import inspect
import types
import pg4276_current_parent_cost_read as previous
import pg4576_current_fresh_noargs_once as entry

SLOT='pg4598-current-parent-cost-read-v1'


def payload(observed):return entry.observer.bind(previous.payload(observed)).replace(previous.SLOT,SLOT)


def main():
    raw=inspect.getsource(previous.main).replace('pg4220-parent-watch-v1','pg4560-parent-watch-v1')
    parent=types.SimpleNamespace(select_parent=previous.parent.select_parent,SOURCE=entry.SOURCE)
    ns={**vars(previous),'SLOT':SLOT,'payload':payload,'parent':parent}
    exec(compile(raw,'<same current Root cost read>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
