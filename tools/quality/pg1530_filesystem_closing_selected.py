"""Fresh storage-only closing/failure PT before new-source full regression."""
import ast
import inspect
import pg1525_filesystem_selected as transport

def server():
 raw=transport.SERVER.replace('PG1525','PG1530')
 tree=ast.parse(raw)
 for n in tree.body:
  if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name):
   if n.targets[0].id=='EXPECTED':n.value=ast.parse("{'LinuxFilesystemClassifierTest':5,'ResourceScopeTest':8,'LinuxInodeSecurityTest':9}",mode='eval').body
   if n.targets[0].id=='MODULES':n.value=ast.parse("['storage']",mode='eval').body
 raw=ast.unparse(tree)
 marker="'-pl', 'src/schubert-nk-storage,src/schubert-nk-batch', '-am'";assert raw.count(marker)==1
 raw=raw.replace(marker,"'-pl', 'src/schubert-nk-storage'")
 raw=raw.replace("'compileOnlyUnselectedModules': ['protocol', 'bootstrap']","'compileOnlyUnselectedModules': []")
 compile(raw,'<new source storage closing/fault selected>','exec');return raw
def main():
 raw=inspect.getsource(transport.main).replace('PG1525','PG1530').replace('pg1525','pg1530').replace("'expectedTests':101","'expectedTests':22").replace("'expectedSuites':7","'expectedSuites':3").replace('SSC269 production filesystem implementation and all delegated original/runtime IO selected suites','BUG1124 lexical Arena release/primary exception preservation; new classifier5/shared scope8/real inode9')
 ns={**transport.__dict__,'SERVER':server()};exec(compile(raw,'<fresh storage-only PT dispatch>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
