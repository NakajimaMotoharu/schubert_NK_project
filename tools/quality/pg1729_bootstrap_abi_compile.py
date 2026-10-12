"""New version all-source Werror plus actual ABI/liveness independent vectors."""
import inspect
import pg1720_current_bootstrap_compile as old
from pg1728_bootstrap_abi_sources import files,SOURCE,TOOLS,bind

def main():
    raw=inspect.getsource(old.main)
    raw=bind(raw).replace('pg1720','pg1729').replace('pg1719_current_bootstrap_sources_test','pg1728_bootstrap_abi_sources_test').replace('pg1728_current_bootstrap_sources_test','pg1728_bootstrap_abi_sources_test')
    raw=raw.replace("str(target/'Pg1728BootstrapInputTest.java')", "str(target/'Pg1728BootstrapInputTest.java'),str(target/'Pg1728OwnedDatabase.java'),str(target/'Pg1728OwnedDatabaseTest.java'),str(target/'Pg1728BootstrapExpectedTest.java')")
    raw=raw.replace("('input',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1728BootstrapInputTest'])", "('input',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1728BootstrapInputTest']),('expected',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1728BootstrapExpectedTest']),('liveness',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1728OwnedDatabaseTest'])")
    ns={**old.__dict__,'files':files,'SOURCE':SOURCE,'TOOLS':TOOLS}
    exec(compile(raw,'<new Bootstrap ABI compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
