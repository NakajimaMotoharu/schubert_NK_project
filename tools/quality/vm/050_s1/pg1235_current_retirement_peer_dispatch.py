"""Fresh immutable peer-qualified retirement, no old slot/operation replay."""
from pg1228_completed_runtime_dispatch import source as previous

def source():
    s=previous().replace('from pg1224_completed_runtime_sources import generated,SHA as BEFORE','from pg1232_completed_retirement_peer_sources import generated\nfrom pg1224_completed_runtime_sources import SHA as BEFORE')
    # Keep actual source factory import above: only the fixed tool paths/classes
    # get a new generation, not an invented Python module name.
    s=s.replace('Pg1224','Pg1232').replace('pg1224-native-tools-v2','pg1232-native-tools-v1')
    s=s.replace("v.replace('pg1224-native-tools-v1','pg1232-native-tools-v1')","v ")
    s=s.replace('pg1226-frozen-v1','pg1233-frozen-v1').replace('pg1229-runtime-schema-preflight-v2','pg1234-current-retirement-peer-preflight-v1').replace('PG1229-runtime-schema-preflight-v2','PG1234-current-retirement-peer-preflight-v1')
    s=s.replace('pg1228','pg1235').replace('PG1228','PG1235')
    s=s.replace("pre['actualDisjointScopeOracle']", "pre['actualDisjointScopeOracle'] and pre['fixedOldRecoveryPostVerified']")
    compile(s,'<fresh new-generation peer retirement dispatch>','exec');return s

if __name__=='__main__':exec(compile(source(),'<actual new-generation retirement dispatch>','exec'),{'__file__':__file__,'__name__':'__main__'})
