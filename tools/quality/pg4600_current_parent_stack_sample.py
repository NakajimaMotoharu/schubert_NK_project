"""One SSC290 bounded method-only sample of the bound Root; no heap/env/service writes."""
import inspect
import pg4224_same_parent_stack_sample as previous
import pg4576_current_fresh_noargs_once as entry


def payload(expected,slot):return entry.observer.bind(previous.payload(expected,slot))


def main():
    raw=inspect.getsource(previous.main).replace('pg4224-current-parent-stack-','pg4600-current-parent-stack-').replace('pg4220-parent-watch-v1','pg4560-parent-watch-v1')
    ns={**vars(previous),'SOURCE':entry.SOURCE,'payload':payload}
    exec(compile(raw,'<same-source original Root one method sample>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
