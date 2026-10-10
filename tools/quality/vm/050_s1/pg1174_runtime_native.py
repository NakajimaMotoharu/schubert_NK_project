"""New canonical zz runtime operator; no old prepare/reload replay."""
import ast
from pg1162_runtime_native import source as previous


def source():
    s=previous().replace('pg1161-runtime-frozen-v1.safe.json','pg1173-runtime-frozen-v1.safe.json').replace('pg1160-runtime-tools-v1','pg1172-runtime-tools-v1').replace('Pg1160RuntimeResume','Pg1172RuntimeResume').replace('pg1162','pg1174').replace('PG1162','PG1174')
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<new correct existing zz runtime>','exec'),{'__file__':__file__,'__name__':'__main__'})
