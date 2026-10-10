"""New-only qualified fixed UTC compiler; actual original tuple eighteen vectors."""
import inspect
import pg1248_fresh_owned_stop_compile as previous
from pg1253_fresh_owned_stop_sources_v2 import sources

def source():
    s=inspect.getsource(previous.main).replace('Pg1247','Pg1253').replace('pg1248','pg1254')
    s=s.replace("'Pg1253StopLabelTest.java']", "'Pg1253StopLabelTest.java','Pg1253OriginalTupleTest.java']")
    s=s.replace("('label','Pg1253StopLabelTest')", "('label','Pg1253StopLabelTest'),('original','Pg1253OriginalTupleTest')")
    compile(s,'<actual complete fresh original tuple compiler>','exec');return s

def main():
    recovered=previous.json.loads((previous.W/'pg1252-fresh-stop-fixed-handoff-v1.safe.json').read_bytes())
    if recovered['actualExit']!=0 or not recovered['oldMgmtPeerAdvisoryFlocks0']or not recovered['full24Full32Signed187StartupOriginalBackupNativeUnchanged']:raise ValueError('actual fixed old scope full post required')
    env=dict(previous.__dict__);env['sources']=sources;env['TARGET']=previous.W/'pg1253-native-tools-v1'
    exec(compile(source(),'<new-only fixed UTC compile actual>', 'exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
