"""Current D5 ABI plus actual CLI/owned DB-label before runtime mutation."""
import ast
import inspect
import pg1199_current_stop_compile as original

def source():
    s=inspect.getsource(original)
    s=s.replace('from pg1198_current_stop_binding import generate, SOURCE, BEFORE, OWNED','from pg1224_completed_runtime_sources import generated\nfrom pg1216_current_full32_stop_binding import SOURCE,BEFORE,OWNED\ndef generate(ignored):return generated()')
    s=s.replace('pg1198_current_stop_binding_test.py','pg1224_completed_runtime_sources_test.py').replace('Pg1198','Pg1224').replace('pg1198-native-tools-v1','pg1224-native-tools-v1').replace('pg1199','pg1225')
    s=s.replace("generated=generate(proof())","post=json.loads((W/'pg1220-full32-terminal-post-v1.safe.json').read_bytes())\n    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']:raise ValueError('current completed post required')\n    generated=generate(None)")
    s=s.replace("'genuineParentBeforeSha256':BEFORE","'completedBeforeSha256':'21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36'")
    s=s.replace("if name.endswith('.py'):ast.parse(raw)","if name.endswith('.py'):compile(raw,'<actual '+name+'>','exec')")
    s=s.replace("str(target/'Pg1224NativeArgumentTest.java')","str(target/'Pg1224NativeArgumentTest.java'),str(target/'Pg1224StopLabelTest.java')")
    s=s.replace("'Pg1224NativeArgumentTest'])]:","'Pg1224NativeArgumentTest']),('label',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1224StopLabelTest'])]:")
    compile(s,'<current retirement compiler>','exec');return s

if __name__=='__main__':exec(compile(source(),'<actual retirement compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
