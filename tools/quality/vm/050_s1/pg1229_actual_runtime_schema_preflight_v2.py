"""New-only corrected run identity; old1227 result remains untouched."""
import inspect
import pg1222_completed_retirement_preflight as transport
import pg1227_actual_runtime_schema_preflight as schema

def payload():
    s=schema.payload().replace('PG1227-runtime-schema-preflight-v1','PG1229-runtime-schema-preflight-v2')
    compile(s,'<fresh current schema trace>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1229-runtime-schema-preflight-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<corrected new-only schema trace transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
