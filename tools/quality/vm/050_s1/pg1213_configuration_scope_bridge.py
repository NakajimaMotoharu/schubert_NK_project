"""Explicit20/state18/full32 join; preserve historical scope, add full before."""
from pg847_configuration import FIELDS as FULL

LEGACY=frozenset('ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictSUIDSGID,CapabilityBoundingSet,AmbientCapabilities,UMask,LimitCORE,TimeoutStartUSec,TimeoutStopUSec,MemoryMax,TasksMax'.split(','))
STATE=frozenset('Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL'.split(','))


def extend(old,current,state):
    if type(old)is not dict or type(current)is not dict or type(state)is not dict or set(old)!=LEGACY or set(current)!=FULL:
        raise ValueError('exact historical20/current32 scope required')
    if any(type(v)is not str for v in [*old.values(),*current.values(),*state.values()])or not STATE<=set(state):
        raise ValueError('complete string fields and state join required')
    if any(old[k]!=current[k]for k in LEGACY)or any(state[k]!=current[k]for k in STATE):
        raise ValueError('historical common fields changed')
    return dict(current),{'historicalConfigurationFields':20,'stateJoinedFields':6,'newlyObservedFields':sorted(FULL-LEGACY-STATE),'currentCapturedFields':32,'historicalFull32Accepted':False}
