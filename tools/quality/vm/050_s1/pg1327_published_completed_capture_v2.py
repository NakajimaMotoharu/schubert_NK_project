"""New-only capture after BUG1077 physical17 independent fixture correction."""
import inspect
import pg1323_published_completed_capture as previous


def payload():
    code=previous.payload().replace('published-completed-capture-v1','published-completed-capture-v2')
    compile(code,'<actual corrected physical17 current fullcapture>','exec');return code


def main():
    env=dict(previous.transport.__dict__,payload=payload)
    code=inspect.getsource(previous.transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1327-published-completed-capture-v2')
    exec(compile(code,'<new-only corrected current capture>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
