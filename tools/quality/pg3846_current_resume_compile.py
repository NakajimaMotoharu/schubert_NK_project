"""Host-only whole current resume ABI from actual current shared classes and signed jars."""
import inspect
import types
import pg3566_current_browser_resume_compile as previous
import pg3844_current_resume_sources as role

TARGET=role.W/role.TOOLS


def main():
    raw=role.bind(inspect.getsource(previous.main)).replace('pg3522-frozen-v1.safe.json','pg3824-frozen-v1.safe.json').replace("name.startswith('Pg3520')","name.startswith('Pg3822')")
    values={**previous.__dict__,'TARGET':TARGET,'SOURCE':role.SOURCE,'BOM':role.BOM,'BEFORE':role.BEFORE,'CURRENT':role.CURRENT,'TOOLS':role.TOOLS,'sources':role.sources}
    values['write']=types.FunctionType(previous.write.__code__,values)
    exec(compile(raw,'<current7fff resume full Java ABI>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
