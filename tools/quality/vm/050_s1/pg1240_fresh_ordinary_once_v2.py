"""New-only guard slot after observer command/exe lexical correction."""
import inspect
import pg1239_fresh_ordinary_once as previous
import pg1236_completed_runtime_retired_post as transport

def payload():
    s=previous.payload().replace('pg1239-fresh-ordinary-once-v1','pg1240-fresh-ordinary-once-v2').replace('PG1239-fresh-ordinary-once-v1','PG1240-fresh-ordinary-once-v2')
    compile(s,'<actual fresh Root v2 command join>','exec');return s

def main():
    if not(previous.W/'pg1237-watch-v1.started').exists()or(previous.W/'pg1237-watch-v1.exit').exists():raise ValueError('existing live qualified observer required')
    watch=previous.W/'pg1237-parent-watch-v1.private.jsonl'
    if not watch.exists()or not watch.stat().st_size:raise ValueError('actual watch frames required')
    entry=inspect.getsource(transport.main).replace('pg1236-completed-runtime-retired-post-v1','pg1240-fresh-ordinary-once-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only current one normal start>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
