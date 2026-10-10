"""Freeze v2 ownedstop plus actual constructor/SQL oracle, no guest mutation."""
import ast
import inspect
import pg1199_current_stop_compile as previous


def source():
    s=inspect.getsource(previous).replace('from pg1198_current_stop_binding','from pg1208_current_stop_v2_binding')
    s=s.replace('pg1198_current_stop_binding_test.py','pg1208_current_stop_v2_binding_test.py').replace('Pg1198','Pg1208').replace('pg1198-native-tools-v1','pg1208-native-tools-v1').replace('pg1199','pg1209')
    s=s.replace("    return dict(d,productionSource=SOURCE,", "    recovery=json.loads((W/'pg1207-failed-stop-metadata-handoff-v1.safe.json').read_bytes())\n    if recovery['actualExit']!=0 or not recovery['newMetadataReferencesNormalClose'] or not recovery['allOldMaintenanceAdmissionPeersAdvisory0']:raise ValueError('current recovery all post required')\n    return dict(d,normalMetadataRecoveryAfterSha256=recovery['privateAfterSha256'],recoveryActualExit=recovery['actualExit'],productionSource=SOURCE,")
    s=s.replace("str(target/'Pg1208NativeArgumentTest.java')", "str(target/'Pg1208NativeArgumentTest.java'),str(target/'Pg1208StopLabelTest.java')")
    s=s.replace("'Pg1208NativeArgumentTest'])]:", "'Pg1208NativeArgumentTest']),('label',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1208StopLabelTest'])]:")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<v2 stop constructor-qualified compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
