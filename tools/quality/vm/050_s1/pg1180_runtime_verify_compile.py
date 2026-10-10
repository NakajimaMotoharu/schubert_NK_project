"""New-only current ABI compile for canonical runtime verify, not preparation."""
import ast
from pg1173_runtime_compile import source as previous


def source():
    s = previous().replace('from pg1172_runtime_sources import files', 'from pg1179_runtime_verify_sources import files').replace('pg1172-runtime-tools-v1', 'pg1179-runtime-tools-v1').replace('pg1173-runtime-frozen-v1', 'pg1180-runtime-verify-frozen-v1').replace('PG1173-runtime-compile-v1', 'PG1180-runtime-verify-compile-v1').replace("'pg1172*test.py'", "'pg1179*test.py'")
    ast.parse(s);return s


if __name__ == '__main__':exec(compile(source(), '<canonical runtime verify compile>', 'exec'), {'__file__': __file__, '__name__': '__main__'})
