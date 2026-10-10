"""Correct basename/existing directory current ABI compile, all writer faults."""
import ast
from pg1161_runtime_compile import source as previous


def source():
    s=previous().replace('from pg1160_runtime_sources import files','from pg1172_runtime_sources import files').replace('pg1160-runtime-tools-v1','pg1172-runtime-tools-v1').replace('pg1161-runtime-frozen-v1','pg1173-runtime-frozen-v1').replace('PG1161-runtime-compile-v1','PG1173-runtime-compile-v1').replace("'pg1160*test.py'","'pg1172*test.py'")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<correct existing runtime compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
