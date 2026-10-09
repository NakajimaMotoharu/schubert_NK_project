"""Single assembled template; new probe/scope source, whole Werror/current750 ABI."""
from pathlib import Path
from pg798_probe_sources import bind

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg778_compile.py').read_text().replace('Pg778FailedRecovery','Pg798DatabaseProbe').replace('pg778','pg798').replace('PG778','PG798')
    raw=raw.replace('import pg798_sources as p','import pg798_probe_sources as p').replace('pg798-failed758-tools-v1','pg798-scope-tools-v1')
    raw=raw.replace("W/'pg777-failure-full758-v1.exit'","W/'pg787-retired-post-v1.exit'").replace("'pg798_contract_test.py'","'pg798_probe_test.py'")
    raw=raw.replace("(R/'Pg798DatabaseProbeTest.java').read_text()","(R/'Pg797DatabaseProbeTest.java').read_text().replace('Pg797DatabaseProbe','Pg798DatabaseProbe')").replace("(R/'pg798_refs.py').read_text()","refs_source()")
    marker="    for name in ('pg481_native_owned_stop.py'"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"    for name in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java','Pg798ProbeWiringTest.java'):sources[name]=(R/name).read_text()\n"+marker)
    raw=raw.replace("str(target/'Pg798DatabaseProbeTest.java')])","str(target/'Pg798DatabaseProbeTest.java'),*[str(target/n)for n in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java','Pg798ProbeWiringTest.java')]])")
    marker="    files={f.name:"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"    with(W/'pg798-pair-oracle-v1.private.log').open('xb')as log:\n        for name in ('Pg797OwnedDatabaseTest','Pg798DatabaseScopeTest','Pg798ProbeWiringTest'):\n            subprocess.run([str(JDK/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,name],stdout=log,stderr=log,check=True)\n        log.flush();os.fsync(log.fileno())\n"+marker)
    raw=raw.replace('80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4','07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2')
    raw=raw.replace("'pythonIndependentAssertions':151","'pairFaultAndWiringOracle':True,'productionPTAdded':0").replace("'pythonAssertions':151","'pairFaultAndWiringOracle':True,'productionPTAdded':0")
    return raw


def refs_source():
    return bind((R/'pg778_refs.py').read_text().replace('pg778','pg797').replace('PG778','PG797')).replace('pg798-failed758-tools-v1','pg798-scope-tools-v1')


if __name__=='__main__':
    exec(compile(source(),'<798 readonly pair full assembly>', 'exec'),{'__file__':str(R/'pg798_probe_compile.py'),'__name__':'__main__','refs_source':refs_source})
