"""New-only qualified v2 canonical zz runtime management."""
import ast
from pg1174_runtime_native import source as previous


def source():
    s=previous().replace('pg1173-runtime-frozen-v1.safe.json','pg1175-runtime-frozen-v2.safe.json').replace('pg1172-runtime-tools-v1','pg1172-runtime-tools-v2').replace('pg1174','pg1176').replace('PG1174','PG1176')
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<new canonical zz v2 scope>','exec'),{'__file__':__file__,'__name__':'__main__'})
