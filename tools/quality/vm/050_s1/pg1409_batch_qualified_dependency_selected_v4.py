"""Reuse qualified unchanged dependency Main bytes, not a repeat build or old failed PT."""
import json
import pg1408_batch_compile_only_selected_v3 as previous

def source():
    raw=previous.source().replace('pg1408','pg1409').replace('PG1408','PG1409')
    old='dependency=subprocess.run(dependency_args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT)'
    if raw.count(old)!=1:raise ValueError('one dependency build-only reuse boundary required')
    raw=raw.replace(old,"saved=json.loads((W/'pg1408-batch-boundary-selected-v1/manifest.safe.json').read_bytes());require(saved['productionMainSource']==SOURCE and saved['dependencyBuildExit']==0 and saved['dependencyMainClassBytesEqual1279']=={'protocol':True,'storage':True,'bootstrap':True})\n        dependency=subprocess.CompletedProcess(dependency_args,0)")
    raw=raw.replace("'dependencyBuildExit':dependency.returncode","'dependencyBuildExit':None,'dependencyNotReissued':True,'dependencyRecordedRun':'PG1408','dependencyRecordedExit':saved['dependencyBuildExit']")
    compile(raw,'<qualified dependency reuse and fresh corrected batch tests>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.previous.__dict__,fresh_xml=previous.previous.fresh_xml,dependency_goals=previous.dependency_goals,GOALS=previous.GOALS)
    exec(compile(source(),'<new corrected batch selection>','exec'),env)
    raise SystemExit(env['main']())
