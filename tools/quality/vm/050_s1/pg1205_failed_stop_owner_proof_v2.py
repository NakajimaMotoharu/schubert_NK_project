"""Whole prior data invariant plus qualified retained GC append, new-only proof."""
import ast
import inspect
import pg1203_failed_stop_owner_proof as previous
import pg1204_jvm_gc_append_oracle as oracle
import pg1120_current_failed_capture as transport


def payload():
    s=previous.prefix().replace("failed-stop-owner-proof-v1'","failed-stop-owner-proof-v2'")
    s+='\nGC_SOURCE='+repr(inspect.getsource(oracle))+'\ngc_oracle=types.ModuleType("independent_gc_append");exec(GC_SOURCE,gc_oracle.__dict__)\n'
    body=previous.BODY.replace('actual==completed_current and actual==capture()and owner==fixed_owner()',
        "all(actual[k]==completed_current[k]for k in actual if k!='journals')and actual==capture()and owner==fixed_owner()")
    body=body.replace(' SAVE.mkdir(mode=0o700)'," gc_result=gc_oracle.qualify(completed_current['journals'],actual['journals'])\n SAVE.mkdir(mode=0o700)")
    body=body.replace(' require(actual==capture()and owner==fixed_owner())',
        " require(actual==capture()and owner==fixed_owner())\n for i,raw_journal in enumerate(JOURNAL_READS):\n  with(SAVE/('journal-read-'+str(i)+'.private.json')).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(raw_journal,sort_keys=True).encode());f.flush();os.fsync(f.fileno())")
    body=body.replace("'wholeCurrentIdentical':True", "'wholeCurrentExceptQualifiedInfoGcIdentical':True,'gcClassification':gc_result")
    s+=body;ast.parse(s);return s


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1205-failed-stop-owner-proof-v2').replace('PG1120-current-failed-capture-v1','PG1205-failed-stop-owner-proof-v2')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<full preserved current owner proof v2>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
