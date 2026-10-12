"""New-only current187 Bootstrap ABI/input preflight freeze; no guest action."""
import inspect
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
import pg894_compile as engine
from pg1719_current_bootstrap_sources import files,SOURCE,TOOLS


def main():
    raw=inspect.getsource(engine.main)
    raw=raw.replace("assert (W/'pg895-bootstrap-before-v1.exit').read_bytes()==b'0\\n'",'')
    raw=raw.replace('pg895-bootstrap-before-v1.safe.json','pg1718-current-bootstrap-before-v1/manifest.safe.json')
    raw=raw.replace("subprocess.run(['python3','-B',str(R/'pg894_source_test.py')],check=True)","subprocess.run(['python3','-B','-m','unittest','pg1719_current_bootstrap_sources_test'],check=True)")
    raw=raw.replace('pg894-bootstrap-tools-v1',TOOLS).replace('Pg894','Pg1719').replace('pg894-'+"'+phase+'-v1",'pg1720-'+"'+phase+'-v1")
    raw=raw.replace('pg894-frozen-v1','pg1720-frozen-v1').replace('pg862-release-v1','pg1638-release-v1')
    raw=raw.replace("str(target/'Pg1719BootstrapArgumentTest.java')", "str(target/'Pg1719BootstrapArgumentTest.java'),str(target/'Pg1719BootstrapInputTest.java')")
    marker="('oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1719BootstrapArgumentTest'])"
    if raw.count(marker)!=1:raise ValueError('one actual independent Bootstrap oracle phase required')
    raw=raw.replace(marker,marker+",('input',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1719BootstrapInputTest'])")
    ns={**engine.__dict__,'files':files,'SOURCE':SOURCE}
    exec(compile(raw,'<current Bootstrap Werror/preownership qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
