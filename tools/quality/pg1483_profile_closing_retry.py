"""Fresh read-only closing after explicit ROOT binding; profiler is not rerun."""
import inspect
import pg1482_partial_profile_closing as previous


def payload():
    raw=previous.payload().replace('pg1482-partial-profile-closing-v1','pg1483-partial-profile-closing-v1').replace('PG1482-partial-profile-closing-v1','PG1483-partial-profile-closing-v1')
    compile(raw,'<fresh readonly closing>','exec');return raw


def main():
    entry=inspect.getsource(previous.main).replace('pg1482-partial-profile-closing-v1','pg1483-partial-profile-closing-v1')
    ns={**previous.__dict__,'payload':payload}
    exec(compile(entry,'<new-only independent closing transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
