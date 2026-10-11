"""Fresh non-mutating verification of created role and corrected closed DB protocol."""
import inspect
import pg1380_bootstrap_role_sources_v3 as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

BASE='pg1391-prepared-role-independent-baseline-v1'
BASE_SHA='37715c53df9f698f1d544233eb8582595b0f90121e583228f8402b92c37f1ac0'

def expected_presence(state,action):
    valid={('READY',b'before'):True,('BEFORE',b'prepared'):True,('PREPARED',b'closed'):False,('CLOSED',b'release'):False}
    if type(state)is not str or type(action)is not bytes or (state,action)not in valid:
        raise ValueError('fixed Ref phase unavailable')
    return valid[(state,action)]

def files():
    result={}
    for name,raw in previous.files().items():
        name=name.replace('1380','1392');raw=raw.replace('Pg1380','Pg1392').replace('pg1380','pg1392').replace('PG1380','PG1392')
        if name.endswith('.java'):
            old='Pg1370BootstrapRoleDirectory.prepare(common,"ordinary-bootstrap196",999,981);'
            new='try(var role=common.openExistingChild("ordinary-bootstrap196")){role.atDirectory(path->{require(Files.getAttribute(path,"unix:uid").equals(999)&&Files.getAttribute(path,"unix:gid").equals(981)&&Files.getAttribute(path,"unix:mode").equals(16832));return Boolean.TRUE;});}'
            if raw.count(old)!=1:raise ValueError('one exact no-mutation held role verification required')
            raw=raw.replace(old,new).replace('HELD_ONE_ROLE','HELD_EXISTING_ROLE').replace('oneBootstrapRolePrepared=true','oneBootstrapRoleVerified=true').replace('oneNewRole=true','existingRoleVerified=true')
        else:
            raw=raw.replace('pg1344-current-bootstrap-before-v1',BASE).replace('f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d',BASE_SHA)
            raw=raw.replace('policy.before_valid(prior)',"require(len(prior)==31 and policy.ROOT+'/'+policy.ROLE in prior)")
            old="action=line.rstrip(b'\\n');require(held==holder(state!='CLOSED'));declaration()"
            if raw.count(old)!=1:raise ValueError('one action/state closed boundary required')
            raw=raw.replace(old,"action=line.rstrip(b'\\n');require(held==holder(expected_presence(state,action)));declaration()")
            raw=raw.replace('policy.delta(prior,now,lower,upper)','require(now==prior)')
            raw=inspect.getsource(expected_presence)+'\n'+raw
        result[name]=raw
    return result
