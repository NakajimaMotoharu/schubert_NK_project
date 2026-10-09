"""Only Requires/After are unordered sets; all remaining fixed fields retain raw bytes."""
FIELDS=frozenset('Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL,TimeoutStartUSec,TimeoutStopUSec,ExecStart,ExecStop,User,Group,SupplementaryGroups,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictAddressFamilies,ReadWritePaths,ReadOnlyPaths,Requires,After,FragmentPath,DropInPaths'.split(','))


def configuration_value(raw):
    if not isinstance(raw,str)or not raw.endswith('\n'):raise ValueError('configuration refused')
    value={}
    for line in raw.splitlines():
        k,sep,v=line.partition('=')
        if not sep or k in value or k not in FIELDS:raise ValueError('configuration refused')
        if k in ('Requires','After'):
            tokens=v.split(' ')if v else []
            if any(not x or any(c.isspace()for c in x)for x in tokens)or len(tokens)!=len(set(tokens)):raise ValueError('dependency set refused')
            v=' '.join(sorted(tokens))
        value[k]=v
    if set(value)!=FIELDS:raise ValueError('configuration fields refused')
    return value
