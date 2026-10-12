"""BUG1141 two phases: no test goal in dependencies, API13 mandatory alone.

Private repository copy contains the new installed dependency jars. Neither
global cache nor old source/target/result is modified or borrowed as a PT pass.
"""
import inspect
import pg1630_api_terminal_selected as prior


def server():
    raw=prior.server().replace('PG1630','PG1634')
    marker="start = datetime.datetime.now(datetime.timezone.utc)"
    if raw.count(marker)!=1:raise ValueError('fixed phase start marker required')
    raw=raw.replace(marker,"""cache=BASE/'m2/repository'
cache_files=[p for p in cache.rglob('*') if p.is_file()]
assert not any(p.is_symlink() for p in cache.rglob('*'))
cache_bytes=sum(p.stat().st_size for p in cache_files)
assert __import__('shutil').disk_usage(BASE).free>=cache_bytes+10*1024**3
cache_hashes={str(p.relative_to(cache)):sha(p) for p in cache_files}
private_repo=OUT/'m2/repository'
__import__('shutil').copytree(cache,private_repo)
assert all(sha(private_repo/n)==h for n,h in cache_hashes.items())
args=[('-Dmaven.repo.local='+str(private_repo)) if v.startswith('-Dmaven.repo.local=') else v for v in args]
pl=args.index('-pl')
common=args[:pl]
dependency_args=common+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','spotless:check','test-compile','jar:test-jar','spotbugs:check','jar:jar','install:install']
api_args=common+['-pl','src/schubert-nk-api','-Dtest='+','.join(EXPECTED),'spotless:check','test-compile','jar:test-jar','test','spotbugs:check','jacoco:report','jar:jar']
args=[dependency_args,api_args]
start = datetime.datetime.now(datetime.timezone.utc)""")
    marker="r = subprocess.run(args, cwd=SOURCE, env=env, stdout=f, stderr=subprocess.STDOUT, umask=23)"
    if raw.count(marker)!=1:raise ValueError('fixed selected execution marker required')
    raw=raw.replace(marker,"""dependency = subprocess.run(dependency_args, cwd=SOURCE, env=env, stdout=f, stderr=subprocess.STDOUT, umask=23)
    r = subprocess.run(api_args, cwd=SOURCE, env=env, stdout=f, stderr=subprocess.STDOUT, umask=23) if dependency.returncode==0 else dependency""")
    raw=raw.replace("passed = r.returncode == 0", "cache_unchanged=all(sha(cache/n)==h for n,h in cache_hashes.items())\npassed = dependency.returncode==0 and cache_unchanged and r.returncode == 0")
    raw=raw.replace("manifest = {'run':", "manifest = {'dependencyCompileExit':dependency.returncode,'dependencyTestGoalAbsent':True,'privateCacheBytes':cache_bytes,'globalCacheUnchanged':cache_unchanged,'cacheSourceManifestSha256':__import__('hashlib').sha256(json.dumps(cache_hashes,sort_keys=True).encode()).hexdigest(),'run':")
    from pyflakes.api import check
    if check('SOURCE_HEAD=""\n'+raw,'<actual two-phase API thirteen>'):raise ValueError('generated static gate refused')
    compile(raw,'<actual two-phase API thirteen>','exec');return raw


def main():
    raw=inspect.getsource(prior.prior.main).replace('PG1525','PG1634').replace('pg1525','pg1634').replace("'expectedTests':101","'expectedTests':13").replace("'expectedSuites':7","'expectedSuites':4").replace('SSC269 production filesystem implementation and all delegated original/runtime IO selected suites','PG-D412 BUG1141 two phase compile-only no dependency test goal, private cache, exact API13 normal failIfNoTests mandatory')
    ns={**prior.prior.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only actual two-phase selected dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
