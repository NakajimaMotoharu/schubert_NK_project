"""Fresh normal owned scope verifies completed canonical runtime without writes."""
import ast
from pg1174_runtime_native import source as previous


def source():
    s = previous().replace('pg1173-runtime-frozen-v1.safe.json', 'pg1180-runtime-verify-frozen-v1.safe.json').replace('pg1172-runtime-tools-v1', 'pg1179-runtime-tools-v1').replace('Pg1172RuntimeResume', 'Pg1179RuntimeVerify').replace('pg1174', 'pg1181').replace('PG1174', 'PG1181')
    ast.parse(s);return s


if __name__ == '__main__':exec(compile(source(), '<fresh canonical runtime verification>', 'exec'), {'__file__': __file__, '__name__': '__main__'})
