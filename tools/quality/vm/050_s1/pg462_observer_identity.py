"""BUG692/YKT496: authenticate BOTH ordinary actor samples only after actual ready/info.
No process action, credentials or VM authority. Fixed field contract is SS342 SSC164.
"""
def require_ready_identity(process, uid, gid, groups):
    keys={'Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb'}
    assert set(process)==keys and all(isinstance(v,str) for v in process.values())
    assert process['Uid'].split()==[uid]*4 and process['Gid'].split()==[gid]*4
    assert process['Groups'].split()==groups and process['NoNewPrivs']=='1'
    assert all(process[k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))

def authenticate_ready(before, after, health, info, expected_info, uid, gid, groups):
    # An exec/identity transition observed before UP must not kill the observer or certify ready.
    if health!=(200,b'{"status":"UP"}') or info[0]!=200 or info[1]!=expected_info:
        return False
    require_ready_identity(before,uid,gid,groups)
    require_ready_identity(after,uid,gid,groups)
    return True
