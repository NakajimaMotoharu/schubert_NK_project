"""Compile-only dependency modules explicitly untested; exact seven required suites mandatory."""
import inspect
import pg1525_filesystem_selected as transport
from pg1526_filesystem_selected_retry import server as previous

def server():
 raw=previous().replace('PG1526','PG1527')
 marker="'-Dsurefire.failIfNoSpecifiedTests=false'";assert raw.count(marker)==1
 raw=raw.replace(marker,marker+",'-DfailIfNoTests=false'")
 compile(raw,'<explicit untested dependency/required selected PT>','exec');return raw
def main():
 raw=inspect.getsource(transport.main).replace('PG1525','PG1527').replace('pg1525','pg1527')
 ns={**transport.__dict__,'SERVER':server()};exec(compile(raw,'<new-only selected required seven suites>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
