"""Immutable v2 current runtime retirement; exactly one entry/reload, starts0."""
from pg1218_current_full32_dispatch import source as previous

def source():
    s=previous();start=s.index('from pg1217_current_full32_compile');end=s.index("W=Path(",start)
    s=s[:start]+IMPORTS+'\n'+s[end:]
    s=s.replace('pg1216-native-tools-v1','pg1224-native-tools-v2').replace('Pg1216','Pg1224').replace('pg1218','pg1228').replace('PG1218','PG1228')
    s=s.replace("(['stage'],['stop'])","(['stage'],['retire'])")
    s=s.replace('stage or stop required','stage or retire required')
    s=s.replace("'pg1217-frozen-v1.safe.json'","'pg1226-frozen-v1.safe.json'").replace("frozen['genuineParentBeforeSha256']","frozen['completedBeforeSha256']")
    s=s.replace("'pg1219-current-full32-preflight-v1.safe.json'","'pg1227-runtime-schema-preflight-v1.safe.json'").replace("pre['fullCurrentBeforeIdentical']","pre['actualDisjointScopeOracle']")
    s=s.replace("'Pg1224NativeStop stop'","'Pg1224NativeStop retire'")
    compile(s,'<current runtime new-only dispatch>','exec');return s

IMPORTS=r'''
from pg1224_completed_runtime_sources import generated,SHA as BEFORE
from pg1216_current_full32_stop_binding import SOURCE
def proof():return {'productionSource':SOURCE,'completedBeforeSha256':BEFORE}
def bindings(value):
 if value!={'productionSource':SOURCE,'completedBeforeSha256':BEFORE}:raise ValueError('current completed identity rejected')
def generate(ignored):return{n:v.replace('pg1224-native-tools-v1','pg1224-native-tools-v2')for n,v in generated().items()}
'''

if __name__=='__main__':exec(compile(source(),'<actual finite retirement dispatch>','exec'),{'__file__':__file__,'__name__':'__main__'})
