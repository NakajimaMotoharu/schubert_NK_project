"""BUG926 fresh immutable v2/compile-v2 only; old compile-v1 retained unaccepted."""
from pathlib import Path
from pg752_sources import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg717_compile.py').read_text()).replace('pg717_sources','pg752_sources')
    raw=replace(raw,(('pg752-compile-v1','pg752-compile-v2'),('pg752-oracle-v1','pg752-oracle-v2'),
                     ('pg752-frozen-v1.safe.json','pg752-frozen-v2.safe.json'),
                     ("'pg752_compile.py'","'pg756_compile.py'")))
    # The generated shell receives the same fresh slots as the outer freeze.
    raw=raw.replace('script = p.compile_script();',"script = p.compile_script().replace('pg752-compile-v1','pg752-compile-v2').replace('pg752-oracle-v1','pg752-oracle-v2');")
    exec(compile(raw,'<correct sequential binding newimmutablev2>', 'exec'),{'__file__':str(R/'pg756_compile.py'),'__name__':'__main__'})
