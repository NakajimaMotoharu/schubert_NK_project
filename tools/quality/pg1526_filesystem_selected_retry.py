"""Fresh explicit qualified four-module reactor; preserve failed parent-plugin campaign."""
import inspect
import pg1525_filesystem_selected as prior

def server():
 raw=prior.SERVER.replace('PG1525','PG1526')
 marker="'-pl','src/schubert-nk-storage,src/schubert-nk-batch','-am'";assert raw.count(marker)==1
 raw=raw.replace(marker,"'-pl',','.join('src/schubert-nk-'+m for m in MODULES)")
 compile(raw,'<explicit offline qualified module PT>','exec');return raw
def main():
 raw=inspect.getsource(prior.main).replace('PG1525','PG1526').replace('pg1525','pg1526')
 ns={**prior.__dict__,'SERVER':server()};exec(compile(raw,'<new-only module PT dispatch>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
