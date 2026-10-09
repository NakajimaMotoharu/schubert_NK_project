"""Fresh current796 owned readonly/75s probe, exact frozen native payload."""
from pathlib import Path
from pg798_probe_native import source as template
from pg804_current_sources import bind
R=Path(__file__).resolve().parent

def source():return bind(template())

if __name__=='__main__':
 import sys
 assert sys.argv[1:]in(['stage'],['verify'])
 exec(compile(source(),'<804 current-source immutable normal scope>', 'exec'),{'__file__':str(R/'pg804_current_native.py'),'__name__':'__main__'})
