"""New-only fixed779 compilation; original778 immutable slot is never recompiled."""
from pathlib import Path
from pg779_sources import bind
from pg777_failure_full import REFERENCE

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg778_compile.py').read_text())
    raw=raw.replace("(R/'Pg779FailedRecoveryTest.java').read_text()", "java_test()")
    raw=raw.replace("(R/'pg779_refs.py').read_text()", "refs_source()")
    def java_test():
        test=bind((R/'Pg778FailedRecoveryTest.java').read_text())
        target='    System.out.println("PG779_JAVA_ORACLE '
        index=test.index(target)
        return test[:index]+'''    Pg779FailedRecovery.refsHeld=true;
    for(String phase:List.of("HELPER_LIVE_VERIFY","BEFORE_PRESERVATION","CURRENT_NAMESPACE","DATABASE_BODY","REFERENCE_ACQUIRE","REFERENCE_CLOSE"))check(Pg779FailedRecovery.retainRequired(phase,false,new Exception("literal failure")));
    Pg779FailedRecovery.refsHeld=false;check(!Pg779FailedRecovery.retainRequired("DATABASE_BODY",false,new Exception("literal")));
'''+test[index:]
    def refs_source():return bind((R/'pg778_refs.py').read_text())
    env={'__file__':str(R/'pg779_compile.py'),'__name__':'__main__','java_test':java_test,'refs_source':refs_source,'REFERENCE':REFERENCE}
    exec(compile(raw,'<new779 immutable compilation>','exec'),env)
