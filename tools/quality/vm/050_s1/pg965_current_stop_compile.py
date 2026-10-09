"""Freeze current-source owned stop only after actual new genuine/A01 proofs."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg877_compile.py').read_text()
    for a,b in (('pg877_stop_binding','pg963_current_stop_binding'),('pg877_binding_test','pg964_current_stop_test'),('Pg877','Pg963'),('pg877','pg963'),('pg875','pg960'),('pg876','pg961'),('pg862','pg932')):
        assert a in raw,a;raw=raw.replace(a,b)
    # Old immutable helper ABI is checked byte-for-byte; production classpath is new PG932.
    # No old genuine/native data is copied or credited to the new source.
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<965 current owned-stop freeze>','exec'),{'__file__':str(R/'pg965_current_stop_compile.py'),'__name__':'__main__'})
