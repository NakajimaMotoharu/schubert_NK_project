"""Fresh-only correct XML count; failed1749 output remains immutable."""
import inspect
import pg1625_unsupported_ports_selected as engine
from pg1749_expiry_observation_selected import server as old_server, FILES as OLD_FILES
from pg1719_current_bootstrap_sources import SOURCE

SLOT='pg1750-expiry-count-selected-v1'
FILES=[p.replace('Pg1749ExpiryObservationLauncher','Pg1750ExpiryObservationLauncher')for p in OLD_FILES]

def main():
    launcher=(engine.ROOT/'tools/quality/vm/050_s1/Pg1750ExpiryObservationLauncher.java').read_text()
    if 'expected.size()' not in launcher or 'tests=\\"2' in launcher or launcher.count('expiry174900')!=4:
        raise ValueError('fixed literal method/count source preflight required')
    server=old_server().replace('PG1749','PG1750').replace('Pg1749ExpiryObservationLauncher','Pg1750ExpiryObservationLauncher')
    raw=inspect.getsource(engine.main).replace('PG1625','PG1750').replace('pg1625','pg1750')
    raw=raw.replace('pg1618-current-ordinary-native-qualified-v3','pg1735-current-bootstrap-native-qualified-v1').replace('pg1624-same-source-native-campaign-v1','pg1735-current-bootstrap-native-qualified-v1')
    ns={**engine.__dict__,'FILES':FILES,'SLOT':SLOT,'SERVER':server,'SOURCE':SOURCE}
    exec(compile(raw,'<new XML count four transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
