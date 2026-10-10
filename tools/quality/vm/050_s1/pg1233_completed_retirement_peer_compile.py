"""New immutable peer-closure compiler after fixed old scope recovery."""
from pg1225_completed_retirement_compile import source as previous

def source():
    s=previous().replace('from pg1224_completed_runtime_sources import generated','from pg1232_completed_retirement_peer_sources import generated')
    s=s.replace('pg1224_completed_runtime_sources_test.py','pg1232_completed_retirement_peer_sources_test.py').replace('Pg1224','Pg1232').replace('pg1224-native-tools-v1','pg1232-native-tools-v1').replace('pg1225','pg1233')
    s=s.replace('generated=generate(None)',"recovery=json.loads((W/'pg1231-current-retirement-handoff-v1.safe.json').read_bytes())\n    if recovery['actualExit']!=0 or recovery['privateAfterSha256']!='4a09d2fab4346eef21b0505fcd656ed65d78520801fcc0736d5c313e5fab0f4d' or not recovery['allClientAdvisoryFlocks0'] or not recovery['newMetadataReferencesNormalClose']:raise ValueError('fixed old scope full post required')\n    generated=generate(None)")
    compile(s,'<new actual peer compiler>','exec');return s

if __name__=='__main__':exec(compile(source(),'<new current peer compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
