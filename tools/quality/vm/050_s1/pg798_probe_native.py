"""One-pass native surface; no runtime deployment/start/retirement action."""
from pathlib import Path
R=Path(__file__).resolve().parent


def source():
    return (R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg798DatabaseProbe').replace('pg778','pg798').replace('PG778','PG798').replace('pg798-failed758-tools-v1','pg798-scope-tools-v1')


if __name__=='__main__':
    import sys
    assert sys.argv[1:]in (['stage'],['verify'])
    exec(compile(source(),'<798 readonly native exact payload>', 'exec'),{'__file__':str(R/'pg798_probe_native.py'),'__name__':'__main__'})
