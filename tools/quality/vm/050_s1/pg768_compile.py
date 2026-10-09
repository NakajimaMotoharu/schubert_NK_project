"""Current767 acceptedbaseline only; new immutable ADMIN and paircontract beforeVM."""
from pathlib import Path
from pg768_sources import current
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source(proof=None,baseline=None):
    # pg737_sources first renames templates; use its full compiler binding.
    from pg737_sources import current as previous
    raw=current(previous((R/'pg662_compile.py').read_text().replace('pg662','pg664').replace('Pg662','Pg664')),proof,baseline)
    marker="    subprocess.run(['/bin/bash','-s'],input=compile_script().encode(),check=True)"
    addition="""    for name in ('pg535_bootstrap_contract.py',):
        with (root/name).open('x')as f:
            os.fchmod(f.fileno(),0o400);f.write(python_files()[name]);f.flush();os.fsync(f.fileno())
"""
    raw=replace(raw,((marker,addition+marker),
        ("'pg570_directory_identity_test.py')", "'pg570_directory_identity_test.py','pg768_pair_contract_test.py')")))
    return raw.replace('from pg768_sources import java, refs, receipt, join, argument_test, compile_script',
        'from pg768_sources import java, refs, receipt, join, argument_test, compile_script,python_files')


if __name__=='__main__':
    exec(compile(source(),'<current newADMIN compile>','exec'),{'__file__':str(R/'pg768_compile.py'),'__name__':'__main__'})
