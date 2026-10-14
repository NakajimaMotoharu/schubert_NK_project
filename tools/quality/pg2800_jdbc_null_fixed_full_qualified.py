"""Independent fresh3680/542/1643/static6, explicit Main delta; no native portability claim."""
import inspect
import pg2772_db_contract_full_qualified as prior
from pg2798_jdbc_null_fixed_full_six import SOURCE, validate


def server():
    raw=prior.server().replace('PG2770','PG2798').replace('3673','3680').replace('541','542').replace(
        "'batch':(1273,172,568)","'batch':(1280,173,568)").replace('04207efc3ad78bca75942153a90c70985064c988',SOURCE)
    start=raw.index('require(set(changed)=={')
    end=raw.index('\nDEBUG_SOURCE=',start)
    # Keep every member, not a filter/exclusion. Candidate Main source is confined by validate.
    # Historical exact seven remain, plus members of the one genuinely changed Main source.
    original=raw[start:end]
    literal=original.removeprefix('require(set(changed)==').removesuffix(')')
    block="""historical="""+literal+"""
morning_prefix='batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession'
require(all(p in historical or p.startswith(morning_prefix)for p in changed))
require(historical<=set(changed))
require(morning_prefix+'$Rows.class'in changed)
"""
    raw=raw[:start]+block+raw[end:]
    raw=raw.replace("'semanticChangedClasses':6,'debugOnlyChangedClasses':1", "'semanticChangedClasses':None,'debugOnlyChangedClasses':1,'physicalChangedClassCount':len(changed),'changedMainMemberQualificationPending':True")
    raw=raw.replace('print(json.dumps(',"require(len([p for p in changed if p.startswith(morning_prefix)])>=3)\nprint(json.dumps(")
    compile(raw,'<fresh changed Main whole independent qualification>','exec');return raw


def main():
    engine=prior.previous.previous.previous
    raw=inspect.getsource(engine.main).replace('pg2651-operation-post-full-qualified-v1',
        'pg2800-jdbc-null-fixed-full-qualified-v1').replace('pg2650-server-six-v1',
        'pg2798-server-six-v1').replace('PG2650','PG2798')
    ns={**engine.__dict__,'SOURCE':SOURCE,'validate':validate,'server':server}
    exec(compile(raw,'<fresh changed Main all XML/input qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
