"""BUG1040 fixed real-FD fault scope; never overwrite failed v1/v2."""
import ast
from pg1150_native_five_compile_v2 import source as previous


def source():
    text=previous().replace('pg1148-native-five-tools-v2','pg1148-native-five-tools-v3').replace('pg1150-native-five-frozen-v2','pg1151-native-five-frozen-v3').replace('PG1150-native-five-compile-v2','PG1151-native-five-compile-v3')
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<new-only native fault scoped compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
