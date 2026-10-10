"""New immutable runtime tools/slots; once owned prepare, no business start."""
import ast
from pg1158_native_five_native_v2 import source as previous


def source():
    s=previous().replace('pg1156-native-five-frozen-v4.safe.json','pg1161-runtime-frozen-v1.safe.json').replace('pg1148-native-five-tools-v4','pg1160-runtime-tools-v1').replace('Pg1148NativeRolePreparation','Pg1160RuntimeResume').replace('pg1158','pg1162').replace('PG1158','PG1162').replace("len(frozen['phases'])==3","len(frozen['phases'])==2")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<new finite runtime transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
