"""New full32 sealed stop ABI compile plus exact constructor/SQL oracle."""
import ast
from pg1209_current_stop_v2_compile import source as previous


def source():
    s=previous().replace('from pg1208_current_stop_v2_binding','from pg1216_current_full32_stop_binding').replace('pg1208_current_stop_v2_binding_test.py','pg1216_current_full32_stop_binding_test.py')
    s=s.replace('Pg1208','Pg1216').replace('pg1208-native-tools-v1','pg1216-native-tools-v1').replace('pg1209','pg1217')
    marker='    return dict(d,normalMetadataRecoveryAfterSha256='
    if s.count(marker)!=1:raise ValueError('fixed full32 actual post qualification insertion refused')
    s=s.replace(marker,"    full=json.loads((W/'pg1215-full32-owner-handoff-v1.safe.json').read_bytes())\n    if full['actualExit']!=0 or not full['newMetadataReferencesNormalClose'] or not full['allFull32ConfigurationRetained'] or not full['oldPeersAdvisoryMaintenanceAdmission0']:raise ValueError('full32 normal actual post required')\n    return dict(d,full32RecoveryAfterSha256=full['privateAfterSha256'],full32RecoveryActualExit=full['actualExit'],normalMetadataRecoveryAfterSha256=")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<full32 fixed compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
