"""Fresh observation after refused old stage; no stop/app/DB mutations."""
import inspect
import pg1330_published_owned_stop_preflight as previous

def payload():
    code=previous.payload().replace('published-stop-preflight-v1','published-stop-preflight-v2')
    compile(code,'<fresh same-cohort reauthentication>','exec');return code

def main():
    env=dict(previous.previous.previous.transport.__dict__,payload=payload)
    code=inspect.getsource(previous.previous.previous.transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1338-published-stop-preflight-v2')
    exec(compile(code,'<new-only fresh current preflight>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
