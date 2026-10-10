"""Current full32 preflight/current immutable tools only, then once owned stop."""
import ast
from pg1212_current_stop_v2_dispatch import source as previous


def source():
    s=previous().replace('from pg1209_current_stop_v2_compile','from pg1217_current_full32_compile').replace('from pg1208_current_stop_v2_binding','from pg1216_current_full32_stop_binding')
    s=s.replace('pg1208','pg1216').replace('Pg1208','Pg1216').replace('pg1209-frozen-v1','pg1217-frozen-v1').replace('pg1212','pg1218').replace('PG1212','PG1218')
    s=s.replace('pg1211-current-stop-preflight-v2','pg1219-current-full32-preflight-v1')
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<full32 newonly actual stop>','exec'),{'__file__':__file__,'__name__':'__main__'})
