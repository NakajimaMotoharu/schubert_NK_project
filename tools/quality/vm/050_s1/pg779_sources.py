"""New immutable SSC235 revision after933/934; old778 failed and closeunknown preserved."""
from pg778_sources import java as prior_java,helper as prior_helper
from pg778_sources import SOURCE as SOURCE,DIGEST as DIGEST


def bind(raw):return raw.replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779')


def java():
    raw=bind(prior_java()).replace('pg779_timeout_owned.py','pg779_owned.py')
    assert raw.count('static boolean touched;')==1
    raw=raw.replace('static boolean touched;','static boolean touched;\n  static boolean refsHeld;')
    raw=raw.replace('return mutated || at.startsWith("REFERENCE_")','return refsHeld || mutated || at.startsWith("REFERENCE_")')
    raw=raw.replace('var refs=new References(db,verify);','refsHeld=true;var refs=new References(db,verify);')
    raw=raw.replace('refs.release();db.rollback();','refs.release();refsHeld=false;db.rollback();')
    for text in ('pg779_owned.py','refsHeld=true;var refs=','refsHeld=false;db.rollback();','return refsHeld ||'):
        assert text in raw
    return raw


def helper():return bind(prior_helper())
