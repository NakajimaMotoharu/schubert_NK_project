"""Fresh immutable typed-retirement v2, no old operator replay."""
import ast
from pg1168_wrong_runtime_native import source as previous


def source():
    s=previous().replace('pg1167-runtime-frozen-v1.safe.json','pg1169-runtime-frozen-v2.safe.json').replace('pg1166-runtime-tools-v1','pg1166-runtime-tools-v2').replace('pg1168','pg1170').replace('PG1168','PG1170').replace("len(frozen['phases'])==2","len(frozen['phases'])==3")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<single new typed retirement v2>','exec'),{'__file__':__file__,'__name__':'__main__'})
