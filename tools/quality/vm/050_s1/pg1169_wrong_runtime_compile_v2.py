"""New-only typed real FD retirement oracle before VM mutation."""
import ast
from pg1167_wrong_runtime_compile import source as previous


def source():
    s=previous().replace('pg1166-runtime-tools-v1','pg1166-runtime-tools-v2').replace('pg1167-runtime-frozen-v1','pg1169-runtime-frozen-v2').replace('PG1167-runtime-compile-v1','PG1169-runtime-compile-v2')
    s=s.replace('write(OUT / name, text.encode())',"write(OUT / name, text.replace('pg1166-runtime-tools-v1','pg1166-runtime-tools-v2').encode())")
    marker="*sorted(java)]),\n]"
    if s.count(marker)!=1:raise ValueError('fixed typed runtime oracle insertion refused')
    s=s.replace(marker,"*sorted(java)]),\n('typed-runtime-oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'dev.codex.schubert.nk.batch.file.Pg1166WrongRuntimeEntryTest'])]")
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<new typed retirement oracle compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
