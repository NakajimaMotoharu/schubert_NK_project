"""Host-only immutable prepared-path tests/static manifest; not real VM/native acceptance."""
import datetime
import hashlib
import io
import json
import os
import platform
import subprocess
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE

MODULES=['pg2226_newboot_fresh_day_before_test','pg2227_newboot_fresh_day_once_test','pg2230_newboot_current_live_binding_test','pg2234_newboot_fresh_day_terminal_test','pg2240_newboot_fresh_day_rows_test','pg2242_newboot_fresh_day_full_seal_test','pg2246_newboot_owned_sources_test','pg2248_newboot_owned_dispatch_test','pg2252_newboot_owned_post_test','pg2254_newboot_native_catalog_test','pg2256_newboot_native_qualification_test']
FILES=['pg2226_newboot_fresh_day_before.py','pg2238_newboot_before_selectors.py','pg2240_newboot_fresh_day_rows.py','pg2240_newboot_fresh_day_rows_test.py','pg2242_newboot_fresh_day_full_seal.py','pg2242_newboot_fresh_day_full_seal_test.py','pg2244_newboot_parent_projection.py','pg2246_newboot_owned_sources.py','pg2246_newboot_owned_sources_test.py','pg2247_newboot_owned_compile.py','pg2248_newboot_owned_dispatch.py','pg2248_newboot_owned_dispatch_test.py','pg2252_newboot_owned_post.py','pg2252_newboot_owned_post_test.py','pg2254_newboot_native_catalog.py','pg2254_newboot_native_catalog_test.py','pg2256_newboot_native_qualification.py','pg2256_newboot_native_qualification_test.py']


def main():
    from pathlib import Path
    os.umask(0o077);root=Path(__file__).resolve().parents[2];out=W/'pg2258-newboot-prepared-path-host-v1';out.mkdir(mode=0o700)
    paths=[root/'tools/quality'/p for p in FILES]+[Path(__file__)]
    before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();log=io.StringIO();suite=unittest.TestLoader().loadTestsFromNames(MODULES)
    testids=[]
    def ids(s):
        for x in s:
            if isinstance(x,unittest.TestSuite):ids(x)
            else:testids.append(x.id())
    ids(suite);result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    static=io.StringIO()
    from pyflakes.reporter import Reporter
    issues=sum(check(p.read_text(),str(p),Reporter(static,static))for p in paths)
    after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    actual=0 if result.wasSuccessful()and not result.skipped and len(testids)==result.testsRun==15 and issues==0 and before==after else 1
    value={'actualExit':actual,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip(),'inputHashes':before,'inputsUnchanged':before==after,'startedUTC':start,'endedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'testIds':testids,'staticIssues':issues,'os':platform.platform(),'python':platform.python_version(),'commands':['python3 -B tools/quality/pg2258_newboot_prepared_path_validation.py','unittest exact 11 modules,15 cases; includes four existing receipt regressions','pyflakes 19 host files and emitted graph validators'],'bugs':['BUG1220/YKT986 already separate qualified; this is only future path preparation'],'actualAllocatedPp':None,'actualTokens':None,'vmStartsStopsWrites0':True,'nativeAccepted':False,'formalAccepted':False}
    (out/'host-test.log').write_text(log.getvalue());(out/'static.log').write_text(static.getvalue())
    value['logs']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[out/'host-test.log',out/'static.log']}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in ['actualExit','productionSource','operatorSource','tests','failures','errors','skipped','staticIssues','inputsUnchanged','vmStartsStopsWrites0','nativeAccepted','formalAccepted']}));return actual


if __name__=='__main__':raise SystemExit(main())
