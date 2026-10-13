"""Dedicated cache, compile-only dependencies, mandatory changed batch tests; old slots retained."""
import inspect
import pg2112_caddy_metadata_selected as old

def server():
    raw=old.SERVER.replace('PG2112','PG2116')
    raw=raw.replace('import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET','import datetime,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as ET')
    raw=raw.replace("modules=['protocol','storage','bootstrap','batch']", "modules=['batch']\nrepo=out/'repository'\nrequired=sum(p.stat().st_size for p in (b/'m2/repository').rglob('*')if p.is_file())\nrequire(shutil.disk_usage(b).free>=required+10*1024**3)\nshutil.copytree(b/'m2/repository',repo,symlinks=True)")
    raw=raw.replace("str(b/'m2/repository')","str(repo)").replace("'-am',",'')
    raw=raw.replace(",'-Dsurefire.failIfNoSpecifiedTests=false','-DfailIfNoTests=false'",'')
    old_run="with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)"
    replacement="""dependency_args=args[:args.index('-pl')]+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','spotless:check','compile','jar:jar','install:install']
with(out/'maven.private.log').open('xb')as f:
 dependency=subprocess.run(dependency_args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)
 if dependency.returncode==0:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)
 else:r=subprocess.CompletedProcess(args,dependency.returncode)
"""
    if raw.count(old_run)!=1:raise ValueError('one actual Maven scope required')
    raw=raw.replace(old_run,replacement)
    raw=raw.replace("'sourceInputsStable':same", "'sourceInputsStable':same,'dependencyCompileOnlyExit':dependency.returncode,'dependencyCommand':dependency_args,'dependencyPtCredit':False,'sharedCacheWritten':False")
    compile(raw,'<isolated dependency build and required Caddy tests>','exec')
    return raw

def main():
    raw=inspect.getsource(old.main).replace('PG2112','PG2116').replace('pg2112','pg2116')
    ns={**old.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only split-scope selected entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
