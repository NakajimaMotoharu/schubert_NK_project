"""BUG1041 retained terminal call closure; new-only qualified current compiler."""
import ast
from pg1151_native_five_compile_v3 import source as previous


def source():
    s=previous().replace('pg1148-native-five-tools-v3','pg1148-native-five-tools-v4').replace('pg1151-native-five-frozen-v3','pg1156-native-five-frozen-v4').replace('PG1151-native-five-compile-v3','PG1156-native-five-compile-v4')
    marker="text.replace('pg1148-native-five-tools-v1','pg1148-native-five-tools-v4').encode()"
    if s.count(marker)!=1:raise ValueError('fixed new management save insertion refused')
    s=s.replace(marker,"text.replace('pg1148-native-five-tools-v1','pg1148-native-five-tools-v4').replace('pg1148-native-five-recovery-v1','pg1148-native-five-recovery-v2').encode()")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<native finite retained calls compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
