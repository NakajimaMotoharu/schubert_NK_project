"""BUG1047 fixture exact mode under compiler077, new-only corrected compile."""
import ast
from pg1173_runtime_compile import source as previous


def source():
    s=previous().replace('pg1172-runtime-tools-v1','pg1172-runtime-tools-v2').replace('pg1173-runtime-frozen-v1','pg1175-runtime-frozen-v2').replace('PG1173-runtime-compile-v1','PG1175-runtime-compile-v2')
    s=s.replace('write(OUT / name, text.encode())',"write(OUT / name, text.replace('pg1172-runtime-tools-v1','pg1172-runtime-tools-v2').encode())")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<mode-independent canonical runtime compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
