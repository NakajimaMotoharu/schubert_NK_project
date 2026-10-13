"""BUG1201: new archive/remote/action slots, unchanged qualified15 bytes, explicit current source/BOM."""
import inspect
import os
import sys
import pg2032_fresh_normal_warning_owned_stop_dispatch as prior
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

REMOTE='/home/ubuntu/pg2038-fixed-stage-v1'
ARCHIVE='pg2038-'+prior.TOOLS+'.tar'
STAGE=prior.STAGE.replace('pg2032-fixed-stage-v1','pg2038-fixed-stage-v1').replace('PG1638','PG1846').replace(prior.TOOLS+'.tar',ARCHIVE)
marker="assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846')"
if STAGE.count(marker)!=1:raise ValueError('one actual release guard required')
STAGE=STAGE.replace(marker,marker+"\nmanifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()\nassert hashlib.sha256(manifest).hexdigest()=='ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7'and json.loads(manifest)['source']['commit']=='0fd734195b4d5338f6b7e860e087cce561d49562'")


def run_action(action):
    raw=inspect.getsource(prior.run_action)
    raw=raw.replace("value=node.value.replace('pg1825','pg2031').replace('pg1826','pg2032').replace('pg1827','pg2033')","value=node.value.replace('pg1825','pg2031').replace('pg1826','pg2038').replace('pg1827','pg2039')")
    raw=raw.replace("post['privateBeforeSha256']!=before","post['privateBeforeSha256']!=before")
    # Frozen source functions and class names stay2030; only archive transport must be new-only.
    anchor="raw=raw.replace(old,\"post['privateBeforeSha256']!=before\")"
    if raw.count(anchor)!=1:raise ValueError('one archive transport rewrite boundary required')
    raw=raw.replace(anchor,anchor+"\n    raw=raw.replace(\"archive=P/(TOOLS+'.tar')\",\"archive=P/\"+repr(ARCHIVE))")
    ns={**prior.__dict__,'run_action':run_action,'REMOTE':REMOTE,'STAGE':STAGE,'ARCHIVE':ARCHIVE}
    exec(compile(raw,'<new current explicit stage once transport>','exec'),ns);return ns['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('fixed new stage/stop only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
