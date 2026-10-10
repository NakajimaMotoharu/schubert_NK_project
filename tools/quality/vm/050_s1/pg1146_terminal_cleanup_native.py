"""New-only stage and one fresh terminal Cleanup/revoke/intent management scope."""
import ast
import inspect
import pg1139_failed_recovery_native as prior


def source():
    text=inspect.getsource(prior)
    text=text.replace('from pg1025_cold_owned_native import source as previous','from pg1025_cold_owned_native import source as previous')
    changes=[('pg1138-failed-recovery-frozen-v3.safe.json','pg1145-terminal-frozen-v1.safe.json'),
             ('pg1134-issued-api-tools-v3','pg1144-terminal-tools-v1'),
             ('Pg1134SingleApiIntentTest','Pg1144SingleApiIntentTest'),
             ('Pg1134SingleApiRecovery','Pg1144SingleApiRecovery'),
             ('pg1139-fixed-stage-v1','pg1146-fixed-stage-v1'),
             ('pg1139-stage-v1.exit','pg1146-stage-v1.exit'),
             ("'pg1139-'+action+'-v1'","'pg1146-'+action+'-v1'"),
             ("'pg1139-' + sys.argv[1] + '-v1'","'pg1146-' + sys.argv[1] + '-v1'"),
             ('PG1139_IMMUTABLE_STAGE','PG1146_IMMUTABLE_STAGE'),
             ('pg1139_failed_recovery_native.py','pg1146_terminal_cleanup_native.py'),
             ('PG1139 immutable current failed recovery','PG1146 fresh terminal Cleanup recovery')]
    for old,new in changes:
        if old not in text:raise ValueError('fixed fresh terminal transport insertion refused')
        text=text.replace(old,new)
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<new-only terminal management transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
