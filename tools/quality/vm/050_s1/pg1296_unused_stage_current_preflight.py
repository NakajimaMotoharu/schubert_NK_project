"""Fresh full current ownership immediately before unused candidate placement."""
import inspect
import pg1281_current_readonly_guard as previous


def main():
    env=dict(previous.__dict__)
    env['payload']=lambda:previous.payload().replace('PG1281','PG1296').replace('pg1281','pg1296')
    code=inspect.getsource(previous.main).replace('PG1281','PG1296').replace('pg1281','pg1296')
    exec(compile(code,'<fresh current unused candidate placement preflight>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
