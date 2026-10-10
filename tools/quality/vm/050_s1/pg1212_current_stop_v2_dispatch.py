"""New immutable v2 slots only; constructor oracle precedes actual owned stop."""
import ast
import inspect
import pg1201_current_stop_dispatch as previous


def source():
    s=inspect.getsource(previous).replace('from pg1199_current_stop_compile import proof','from pg1209_current_stop_v2_compile import source as compiler_source\ncompiler={"__name__":"qualified_v2_compile","__file__":__file__};exec(compile(compiler_source(),"<v2 compiler pure definitions>","exec"),compiler);proof=compiler["proof"]')
    s=s.replace('from pg1198_current_stop_binding','from pg1208_current_stop_v2_binding').replace('pg1198','pg1208').replace('Pg1198','Pg1208')
    s=s.replace('pg1199-frozen-v1','pg1209-frozen-v1').replace('pg1200-current-stop-preflight-v1','pg1211-current-stop-preflight-v2')
    s=s.replace('pg1201','pg1212').replace('PG1201','PG1212')
    s=s.replace("commands=[(SSH+[prefix+'Pg1208NativeArgumentTest'],None)", "commands=[(SSH+[prefix+'Pg1208StopLabelTest'],None),(SSH+[prefix+'Pg1208NativeArgumentTest'],None)")
    marker="STAGE=inspect.getsource(archive_members)+'\\n'+STAGE"
    if s.count(marker)!=1:raise ValueError('fixed archive source literal insertion refused')
    s=s.replace(marker,'STAGE='+repr(previous.STAGE.replace('pg1201','pg1212').replace('PG1201','PG1212').replace('pg1198','pg1208')))
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<v2 fixed actual owned stop transport>','exec'),{'__name__':'__main__','__file__':__file__})
