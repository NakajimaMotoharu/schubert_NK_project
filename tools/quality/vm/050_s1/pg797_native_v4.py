"""Direct single template transport; use already compiled307/v3, distinct native-v4 receipts."""
from pathlib import Path
from pg797_sources import bind

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg783ExistingPairRetirement').replace('pg778','pg783').replace('PG778','PG783')
    raw=bind(raw).replace('pg797-failed758-tools-v1','pg797-liveness-tools-v3').replace('pg797-frozen-v1.safe.json','pg797-frozen-v3.safe.json')
    raw=raw.replace("action+'-v1'", "action+'-v4'").replace('pg797-stage-v1.exit','pg797-stage-v4.exit').replace('pg797-fixed-stage-v1','pg797-fixed-stage-v4')
    return raw


if __name__=='__main__':
    import sys
    assert sys.argv[1:]in (['stage'],['verify'])
    exec(compile(source(),'<direct797 native v4 actual payload v3>', 'exec'),{'__file__':str(R/'pg797_native_v4.py'),'__name__':'__main__'})
