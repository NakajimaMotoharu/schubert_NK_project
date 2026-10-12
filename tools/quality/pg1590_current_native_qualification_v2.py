"""New-slot same-byte analysis, exact generated-source static gate, no VM writes."""
import inspect
import pg1587_current_native_qualification as prior

def source():
    raw=inspect.getsource(prior.main)
    raw=raw.replace('pg1586-current-native-catalog-v2','pg1588-current-native-catalog-v3')
    raw=raw.replace('pg1587-current-native-qualified-v1','pg1590-current-native-qualified-v2').replace('PG1587','PG1590')
    old='source=\'import xml.etree.ElementTree as ET\\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\\ndef require(value):\\n if not value:raise ValueError("current coverage XML counter mismatch")\\n\'+source'
    new='source=\'import xml.etree.ElementTree as ET\\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\\n\'+source'
    if raw.count(old)!=1:raise ValueError('one duplicate injected require refused')
    raw=raw.replace(old,new)
    marker="    (out/'server-payload.private.py').write_text(source)"
    replacement=marker+"\n    from pyflakes.api import check\n    from pyflakes.reporter import Reporter\n    import sys\n    if check(source,'<actual current server native payload>',Reporter(sys.stdout,sys.stderr)):raise ValueError('actual assembled source static gate refused')"
    if raw.count(marker)!=1:raise ValueError('actual assembled static gate insertion refused')
    raw=raw.replace(marker,replacement)
    raw=raw.replace("    os.umask(0o077);out=", "    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']):raise ValueError('clean same current source operator required')\n    os.umask(0o077);out=")
    compile(raw,'<static clean independent native analysis>','exec');return raw

def main():
    env={**prior.__dict__,'CODE':prior.CODE.replace('PG1587','PG1590')}
    exec(compile(source(),'<new-only sameSource native static gate>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
