"""SameMain isolated API five; new config-load oracle, current native8 only."""
import inspect
import pg1629_api_main_selected as prior
from pg1700_new_source_live_binding import SOURCE


def server():
    raw=prior.server()
    for old,new in [('PG1629','PG1714'),('Pg1629ApiMainLauncher','Pg1714ApiMainLauncher'),
                    ('PG1532','PG1633'),('PG1618-native-v1','PG1709-native-v1'),
                    ('PG1624-native-campaign-v1','PG1709-native-v1')]:raw=raw.replace(old,new)
    raw=raw.replace("['PG1590-native-v1','PG1709-native-v1']", "['PG1709-native-v1']")
    start=raw.index("old=b/'runs/PG1628-selected-v1'")
    end=raw.index('coverage={};xml_hashes={}',start)
    raw=raw[:start]+raw[end:]
    for old,new in [('tests4','tests5'),("=='4'","=='5'"),('==4)','==5)'),("'tests':4","'tests':5")]:raw=raw.replace(old,new)
    compile(raw,'<current Main isolated API5>','exec')
    return raw


def main():
    engine=prior.prior
    raw=inspect.getsource(engine.main)
    for old,new in [('PG1628','PG1714'),('pg1628','pg1714'),
                    ('pg1618-current-ordinary-native-qualified-v3','pg1709-new-source-native-qualified-v1'),
                    ('pg1624-same-source-native-campaign-v1','pg1709-new-source-native-qualified-v1')]:raw=raw.replace(old,new)
    files=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMainTest.java',
           'tools/quality/vm/050_s1/Pg1714ApiMainLauncher.java',
           'tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']
    ns={**engine.__dict__,'SOURCE':SOURCE,'FILES':files,'SERVER':server(),
        'SLOT':'pg1714-api-configuration-negative-selected-v1'}
    exec(compile(raw,'<current source API5 isolated transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
