"""New-only current terminal management compile; independent old failures kept."""
import ast
from pg1138_failed_recovery_compile_v3 import source as previous


def source():
    text=previous()
    changes=[('from pg1134_failed_recovery_sources import files, SOURCE','from pg1144_terminal_cleanup_recovery_sources import files\nfrom pg1134_failed_recovery_sources import SOURCE'),
             ('pg1134-issued-api-tools-v3','pg1144-terminal-tools-v1'),
             ('pg1138-failed-recovery-frozen-v3','pg1145-terminal-frozen-v1'),
             ('PG1138-failed-recovery-compile-v3','PG1145-terminal-compile-v1'),
             ('Pg1134','Pg1144'),("'pg113[3478]*test.py'","'pg1144*test.py'")]
    for old,new in changes:
        if old not in text:raise ValueError('fixed current terminal compiler insertion refused')
        text=text.replace(old,new)
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<current terminal management compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
