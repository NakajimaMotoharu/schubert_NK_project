"""Dependency compile-only assembly, not formal verify; mandatory selected batch PT unchanged."""
import inspect
import pg1407_batch_boundary_selected_v2 as previous

GOALS=['spotless:check','compile','jar:jar','install:install']

def dependency_goals(value):
    if type(value)is not list or value!=GOALS:raise ValueError('fixed compile-only assembly goals required')
    return list(value)

def source():
    raw=previous.source().replace('pg1407','pg1408').replace('PG1407','PG1408')
    old="'-DskipTests','spotless:check','install']"
    if raw.count(old)!=1:raise ValueError('one explicit dependency lifecycle boundary required')
    raw=raw.replace(old,"]+dependency_goals(GOALS)")
    raw=raw.replace("'dependencyBuildExit':dependency.returncode","'dependencyBuildExit':dependency.returncode,'dependencyCompileOnlyNoPtCredit':True,'formalVerifyNotRun':True")
    compile(raw,'<compile-only dependency and strict target batch PT>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.__dict__,fresh_xml=previous.fresh_xml,dependency_goals=dependency_goals,GOALS=GOALS)
    exec(compile(source(),'<new compile-only batch selection>','exec'),env)
    raise SystemExit(env['main']())
