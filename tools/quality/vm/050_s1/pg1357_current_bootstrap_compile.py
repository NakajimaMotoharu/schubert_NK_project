"""Compile actual Expected constructor vectors before any fresh DB scope."""
from pathlib import Path
from pg1348_current_bootstrap_compile import source as previous
R = Path(__file__).resolve().parent

def source():
    raw = previous().replace('pg1348', 'pg1356').replace('Pg1348', 'Pg1356')
    old = "str(target/'Pg1356BootstrapArgumentTest.java')"
    if raw.count(old) != 1:
        raise ValueError('one actual javac source boundary required')
    raw = raw.replace(old, old + ",str(target/'Pg1356BootstrapDatabaseApplicationTest.java')")
    old = "('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1356BootstrapArgumentTest'])"
    if raw.count(old) != 1:
        raise ValueError('one actual CLI oracle boundary required')
    raw = raw.replace(old, "('db-application-oracle',[str(J/'java'),'-cp',cp,'Pg1356BootstrapDatabaseApplicationTest'])," + old)
    compile(raw, '<new actual DB application vectors>', 'exec')
    return raw

if __name__ == '__main__':
    exec(compile(source(), '<new immutable Bootstrap ABI build>', 'exec'),
         {'__file__': str(R / 'pg1357_current_bootstrap_compile.py'), '__name__': '__main__'})
