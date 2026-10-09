"""New immutable current750 liveness payload, Werror and actual assembled helper/profile checks."""
from pathlib import Path
from pg797_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg778_compile.py').read_text().replace('Pg778FailedRecovery','Pg783ExistingPairRetirement').replace('pg778','pg783').replace('PG778','PG783'))
    raw=raw.replace('pg797-failed758-tools-v1','pg797-liveness-tools-v1').replace("(W/'pg777-failure-full758-v1.exit')", "(W/'pg787-retired-post-v1.exit')")
    raw=raw.replace("'pg797_contract_test.py'", "'pg797_sources_test.py'").replace("(R/'pg797_refs.py').read_text()", "refs_source()")
    raw=raw.replace("'Pg797DatabaseProbeTest.java':(R/'Pg797DatabaseProbeTest.java').read_text(),", "'Pg797DatabaseProbeTest.java':(R/'Pg797DatabaseProbeTest.java').read_text(),'Pg797OwnedDatabase.java':(R/'Pg797OwnedDatabase.java').read_text(),'Pg797OwnedDatabaseTest.java':(R/'Pg797OwnedDatabaseTest.java').read_text(),")
    raw=raw.replace("str(target/'Pg797DatabaseProbeTest.java')", "str(target/'Pg797DatabaseProbeTest.java'),str(target/'Pg797OwnedDatabase.java'),str(target/'Pg797OwnedDatabaseTest.java')")
    raw=raw.replace("'pythonIndependentAssertions':151", "'javaOwnedDatabaseAssertions':299").replace("'pythonAssertions':151", "'javaOwnedDatabaseAssertions':299,'productionPTAdded':0")
    raw=raw.replace('80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4','07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2')
    def refs_source():
        return bind((R/'pg778_refs.py').read_text().replace('pg778','pg783').replace('PG778','PG783')).replace('pg797-failed758-tools-v1','pg797-liveness-tools-v1')
    exec(compile(raw,'<new797 current750 two-session liveness>','exec'),{'__file__':str(R/'pg797_compile.py'),'__name__':'__main__','refs_source':refs_source})
