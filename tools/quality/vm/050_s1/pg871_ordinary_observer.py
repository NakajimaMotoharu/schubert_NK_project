"""Fresh observer for current862/noargs; observe only, never issue start/stop."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg807_parent_observer.py').read_text()
    for old,new in (('pg807','pg871'),('PG807','PG871'),('PG796','PG862'),('pg806-resume-post-v1','pg870-ordinary-before-v1'),('102cdf1d365ab321f74b523237590eee764ae858','e01612fcd7f2752df5ae0836b78538fd5e87f120'),('c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe')):raw=raw.replace(old,new)
    raw=raw.replace("assert(W/'pg870-ordinary-before-v1.exit').read_text()=='0\\n'","assert json.loads((W/'pg870-ordinary-before-v1.safe.json').read_bytes())['actualExit']==0")
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<871 current862 ordinary observer>', 'exec'),{'__file__':str(R/'pg871_ordinary_observer.py'),'__name__':'__main__'})
