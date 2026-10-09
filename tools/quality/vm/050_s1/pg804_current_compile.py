"""Single flattened compile template; fresh current796 source ABI, same scope fault vectors."""
from pathlib import Path
from pg798_probe_compile import source as template,refs_source as original_refs
from pg804_current_sources import bind
R=Path(__file__).resolve().parent

def source():
 raw=bind(template()).replace('import pg804_probe_sources as p','import pg804_current_sources as p').replace('pg804_probe_test.py','pg804_current_test.py').replace("W/'pg787-retired-post-v1.exit'","W/'pg803-published-handoff-v2.exit'")
 raw=raw.replace("'Pg798ProbeWiringTest.java'):sources[name]=(R/name).read_text()", "):sources[name]=(R/name).read_text()\n    sources['Pg804WiringTest.java']=(R/'Pg798ProbeWiringTest.java').read_text().replace('Pg798ProbeWiringTest','Pg804WiringTest').replace('Pg798DatabaseProbe','Pg804CurrentReadback')")
 raw=raw.replace("'Pg798ProbeWiringTest.java')]]","'Pg804WiringTest.java')]]").replace("'Pg798ProbeWiringTest'):","'Pg804WiringTest'):")
 return raw.replace('07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2','d82a4626f8b9a0cb00130087413d1dd227dd04ced4f9add680668f99b27c6a92')

def refs_source():return bind(original_refs())

if __name__=='__main__':
 exec(compile(source(),'<804 same current-source exact namespace>', 'exec'),{'__file__':str(R/'pg804_current_compile.py'),'__name__':'__main__','refs_source':refs_source})
