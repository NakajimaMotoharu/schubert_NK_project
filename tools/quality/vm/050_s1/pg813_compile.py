"""New immutable tools, whole actual current796 ABI/Werror and independent oracles."""
import ast
from pathlib import Path
import pg813_sources as p
R=Path(__file__).resolve().parent
def refs_source():return p.bind((R/'pg778_refs.py').read_text().replace('pg778','pg779').replace('PG778','PG779'))
def source():
 raw=p.bind((R/'pg778_compile.py').read_text().replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779'))
 raw=raw.replace("W/'pg777-failure-full758-v1.exit'","W/'pg812-current-timeout-v4.exit'")
 raw=raw.replace("(R/'Pg813FailedRecoveryTest.java').read_text()",'p.java_test()').replace("(R/'pg813_refs.py').read_text()",'refs_source()')
 marker="    for name in ('pg481_native_owned_stop.py'"
 raw=raw.replace(marker,"    for name in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java'):sources[name]=(R/name).read_text()\n"+marker)
 raw=raw.replace("str(target/'Pg813FailedRecoveryTest.java')])","str(target/'Pg813FailedRecoveryTest.java'),*[str(target/n)for n in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java')]])")
 raw=raw.replace('80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4',p.SNAPSHOT)
 raw=raw.replace('pg813-frozen-v1.safe.json','pg813-frozen-v2.safe.json').replace("'-v1.private.log'","'-v2.private.log'").replace("'-v1.exit'","'-v2.exit'").replace('pg813-database-oracle-v1','pg813-database-oracle-v2').replace('pg813-oracle-v1.private.log','pg813-oracle-v2.private.log')
 marker="    files={f.name:"
 raw=raw.replace(marker,"    with(W/'pg813-database-oracle-v1.private.log').open('xb')as log:\n        for name in ('Pg797OwnedDatabaseTest','Pg798DatabaseScopeTest'):\n            subprocess.run([str(JDK/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,name],stdout=log,stderr=log,check=True)\n        log.flush();os.fsync(log.fileno())\n"+marker)
 raw=raw.replace("'pythonIndependentAssertions':151","'pythonIndependentTests':3,'databaseFaultOracle':True,'productionPTAdded':0").replace("'pythonAssertions':151","'pythonIndependentTests':3,'databaseFaultOracle':True,'productionPTAdded':0")
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<813 single full compiler assembly>','exec'),{'__file__':str(R/'pg813_compile.py'),'__name__':'__main__','refs_source':refs_source})
