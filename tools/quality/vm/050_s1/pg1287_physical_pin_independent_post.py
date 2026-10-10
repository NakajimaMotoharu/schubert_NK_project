"""New-only complete current post after component namespaces; no repeated mutation."""
import inspect
import pg1281_current_readonly_guard as previous


def main():
    env=dict(previous.__dict__)
    env['payload']=lambda:previous.payload().replace('PG1281','PG1287').replace('pg1281','pg1287')
    code=inspect.getsource(previous.main).replace('PG1281','PG1287').replace('pg1281','pg1287')
    exec(compile(code,'<independent physical pin complete current post>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
