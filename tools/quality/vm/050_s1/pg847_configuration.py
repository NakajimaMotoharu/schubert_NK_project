"""BUG967 independent full union contract; execution history never declaration authority."""
FIELDS=frozenset('Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL,TimeoutStartUSec,TimeoutStopUSec,ExecStart,ExecStop,User,Group,SupplementaryGroups,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictAddressFamilies,ReadWritePaths,ReadOnlyPaths,Requires,After,FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax'.split(','))
def same(expected,actual,parse):
 if type(expected)is not dict or type(actual)is not dict or set(expected)!=FIELDS or set(actual)!=FIELDS:return False
 if not all(type(v)is str for v in(*expected.values(),*actual.values())):return False
 for key in FIELDS:
  if expected[key]==actual[key]:continue
  if key not in ('ExecStart','ExecStop'):return False
  left=parse(expected[key]);right=parse(actual[key])
  if left is None or right is None or left[:3]!=right[:3]:return False
 return True
