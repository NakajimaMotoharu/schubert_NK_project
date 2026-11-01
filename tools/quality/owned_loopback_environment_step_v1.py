"""Own-loopback runner environment capture; fixed module, no caller/source qualification cycle."""
from pg14282_current_pt_environment_post import headers
import scoped_prometheus_owned_loopback_host_v1 as run
_owned_original_step=run.step
def environmental_step(name,command):
    result=_owned_original_step(name,command)
    if name=='selected-junit' and result['actualExit']==0:
        log=run.SLOT/'selected-junit.log'
        assert run.host.sha(log)==result['logSha256']
        lines=[]
        with log.open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if not line:break
                lines.append(line)
        assert sum(len(x.encode()) for x in lines)<=4096
        result['reportedEnvironment']=headers(lines)
        result['environmentBasis']='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    return result
