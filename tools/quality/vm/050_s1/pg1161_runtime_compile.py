"""Current1068 immutable helper closure, runtime writer independent host oracle."""
import ast
from pg1156_native_five_compile_v4 import source as previous


def source():
    s=previous().replace('from pg1148_native_five_sources import files','from pg1160_runtime_sources import files')
    s=s.replace('pg1148-native-five-tools-v4','pg1160-runtime-tools-v1').replace('pg1156-native-five-frozen-v4','pg1161-runtime-frozen-v1').replace('PG1156-native-five-compile-v4','PG1161-runtime-compile-v1')
    s=s.replace("'pg1148*test.py'","'pg1160*test.py'")
    marker="text.replace('pg1148-native-five-tools-v1','pg1160-runtime-tools-v1').replace('pg1148-native-five-recovery-v1','pg1148-native-five-recovery-v2').encode()"
    if s.count(marker)!=1:raise ValueError('fixed new runtime source emitter refused')
    s=s.replace(marker,'text.encode()')
    start=s.index("                ('native-five-directory-oracle'");end=s.index('    phases = []',start)
    s=s[:start]+']\n'+s[end:]
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<current finite runtime compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
