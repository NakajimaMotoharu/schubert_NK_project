"""Freeze the complete actual current/new candidate finite publication ABI."""
import inspect
import pg2171_normal_publication_compile as prior
from pg2440_question_normal_publication_sources import sources,TOOLS,BOM,BEFORE,CURRENT,production

TARGET=prior.prior.W/TOOLS


def compiler():
    raw=prior.compiler()
    for a,b in [('pg2168-normal-candidate-ro-post-v1','pg2426-question-candidate-ro-post-v1'),
                ('pg2126-candidate-build','pg2428-candidate-build'),('pg2145-frozen','pg2433-frozen'),
                ('pg2144-current-normal-unused-tools-v1','pg2432-current-boot-question-tools-v1'),
                ('Pg2144','Pg2432'),('pg2170','pg2440'),('Pg2170','Pg2440'),
                ('pg2171-','pg2441-'),('pg1846-release-v1','pg2126-release-v1')]:raw=raw.replace(a,b)
    compile(raw,'<actual current/new finite publication compiler>','exec')
    return raw


def main():
    ns={**prior.prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,
        'CANDIDATE':production(),'OLD':CURRENT,'BOM':BOM,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(prior.prior.write),'<canonical immutable writer>','exec'),ns)
    exec(compile(compiler(),'<current finite publication ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
