"""Single fresh wrong-runtime retirement; never reissue oldprepare/reload."""
import ast
from pg1162_runtime_native import source as previous


def source():
    s=previous().replace('pg1161-runtime-frozen-v1.safe.json','pg1167-runtime-frozen-v1.safe.json').replace('pg1160-runtime-tools-v1','pg1166-runtime-tools-v1').replace('Pg1160RuntimeResume','Pg1166WrongRuntimeRetirement').replace('pg1162','pg1168').replace('PG1162','PG1168')
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<once typed wrong runtime retire>','exec'),{'__file__':__file__,'__name__':'__main__'})
