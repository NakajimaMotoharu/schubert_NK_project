"""New save/tools/slots for fixed live-call native management. Never replay1152."""
import ast
from pg1152_native_five_native import source as previous


def source():
    s=previous().replace('pg1151-native-five-frozen-v3.safe.json','pg1156-native-five-frozen-v4.safe.json').replace('pg1148-native-five-tools-v3','pg1148-native-five-tools-v4').replace('pg1152','pg1158').replace('PG1152','PG1158')
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<new native v2 management>','exec'),{'__file__':__file__,'__name__':'__main__'})
