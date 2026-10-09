"""One new current failed full24 capture, canonical systemd dependency sets only."""
from pathlib import Path
from pg662_sources import replace
from pg774_failure_full import source as prior

R=Path(__file__).resolve().parent


def source():
    pure=(R/'pg775_configuration.py').read_text()
    return replace(prior().replace('pg774-failure-full758-v1','pg775-failure-full758-v1'),
        (('def configurations():',pure+'\ndef configurations():'),
         ("return {u:command(['/usr/bin/systemctl','show',u,'--property='+fields]).decode()for u in units}","return {u:configuration_value(command(['/usr/bin/systemctl','show',u,'--property='+fields]).decode())for u in units}")))


if __name__=='__main__':
    exec(compile(source(),'<new775 allcurrentcapture>','exec'),{'__file__':str(R/'pg775_failure_full.py'),'__name__':'__main__'})
