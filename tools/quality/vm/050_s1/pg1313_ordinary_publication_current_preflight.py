"""New-only current full read-only observation immediately before finite publication."""
import inspect
import pg1281_current_readonly_guard as previous


def main():
    env=dict(previous.__dict__)
    env['payload']=lambda:previous.payload().replace('PG1281','PG1313').replace('pg1281','pg1313')
    code=inspect.getsource(previous.main).replace('PG1281','PG1313').replace('pg1281','pg1313')
    exec(compile(code,'<current publication preflight>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
