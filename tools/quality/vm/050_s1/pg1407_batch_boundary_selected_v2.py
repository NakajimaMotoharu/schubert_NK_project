"""Explicit dependency build-only, strict batch selection and fresh XML, old run unchanged."""
import inspect
import pg1406_batch_boundary_selected as previous

def source():
    raw=inspect.getsource(previous.main).replace('pg1406','pg1407').replace('PG1406','PG1407')
    raw=raw.replace("'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch'","'src/schubert-nk-batch'")
    marker="        if p.exists():shutil.copyfile(p,prior/p.name)"
    if raw.count(marker)!=1:raise ValueError('one fresh XML isolation boundary required')
    raw=raw.replace(marker,"        if p.exists():\n            shutil.copyfile(p,prior/p.name);p.rename(prior/('stale-original-'+p.name))")
    marker="        r=subprocess.run(args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT);f.flush();os.fsync(f.fileno())"
    if raw.count(marker)!=1:raise ValueError('one actual selected build boundary required')
    raw=raw.replace(marker,"""        dependency_args=args[:args.index('-pl')]+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','-DskipTests','spotless:check','install']
        dependency=subprocess.run(dependency_args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT)
        dependency_same={}
        if dependency.returncode==0:
            for module in ('protocol','storage','bootstrap'):
                name='schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'
                dependency_same[module]=class_hashes(W/'pg1279-held-channel-six-host-v1'/module/name)==class_hashes(T/'src'/('schubert-nk-'+module)/'target'/name)
        if dependency.returncode==0 and all(dependency_same.values())and len(dependency_same)==3:
            r=subprocess.run(args,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT)
        else:r=subprocess.CompletedProcess(args,dependency.returncode or 2)
        f.flush();os.fsync(f.fileno())""")
    marker="        x=ET.parse(p).getroot();counts[suite]={k:int(x.attrib[k])for k in ('tests','failures','errors','skipped')}"
    if raw.count(marker)!=1:raise ValueError('one actual XML collection boundary required')
    raw=raw.replace(marker,"        value=fresh_xml(p,suite,int(start.timestamp()*1000000000))\n        if value is None:missing.append(suite);continue\n        counts[suite]=value")
    raw=raw.replace("'staticIssues':static", "'dependencyCommand':dependency_args,'dependencyBuildExit':dependency.returncode,'dependencyMainClassBytesEqual1279':dependency_same,'freshXmlRequired':True,'notRunCount':sum(SUITES[n]for n in missing),'staticIssues':static")
    compile(raw,'<new explicit dependency scope and fresh batch collector>','exec');return raw

def fresh_xml(path,suite,start_ns):
    import xml.etree.ElementTree as ET
    if not path.is_file()or path.is_symlink()or path.stat().st_mtime_ns<start_ns:return None
    root=ET.parse(path).getroot()
    if root.tag!='testsuite'or root.attrib.get('name')!=suite:return None
    return {k:int(root.attrib[k])for k in ('tests','failures','errors','skipped')}

if __name__=='__main__':
    env=dict(previous.__dict__,fresh_xml=fresh_xml)
    exec(compile(source(),'<new strict selected batch execution>','exec'),env)
    raise SystemExit(env['main']())
