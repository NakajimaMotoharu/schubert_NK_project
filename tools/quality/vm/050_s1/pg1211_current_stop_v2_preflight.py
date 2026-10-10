"""New readonly preflight against actual post-metadata recovery full seal."""
import ast
import inspect
import pg1200_current_stop_preflight as previous
import pg1120_current_failed_capture as transport


def payload():
    s=previous.payload().replace("completed-stop-preflight-v1'","completed-stop-preflight-v2'")
    s=s.replace("completed-current-before-v1/before.private.json').read_bytes()", "failed-stop-metadata-handoff-v1/after.private.json').read_bytes()")
    s=s.replace("hashlib.sha256(sealed_raw).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa'", "hashlib.sha256(sealed_raw).hexdigest()=='d85fbf1524fc1edae344b349f7828fac6fd8ff6b763fe635dc1c3b30de4c1247'")
    ast.parse(s);return s


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1211-current-stop-preflight-v2').replace('PG1120-current-failed-capture-v1','PG1211-current-stop-preflight-v2')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<v2 current full post preflight>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
