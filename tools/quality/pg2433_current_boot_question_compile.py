"""New-only complete current boot ABI; old wrong-boot freeze is not repaired in place."""
import types
import pg2413_question_unused_compile as prior
from pg2432_current_boot_question_sources import sources,bind,TOOLS,ARCHIVE as ARCHIVE_NAME,CURRENT,BEFORE,production

TARGET=prior.prior.engine.W/TOOLS
ARCHIVE=prior.prior.engine.P/ARCHIVE_NAME


def compiler():return bind(prior.compiler()).replace('pg2413-','pg2433-')


def validate_actual_graph(target,hashes):
    import inspect
    raw=bind(inspect.getsource(prior.prior.validate_actual_graph))
    # The base declarations still carry their original pg2132 prefix.
    raw=raw.replace('pg2132','pg2432').replace('pg2126-manifest-v1.sig','pg2428-manifest-v1.sig')
    namespace={**prior.prior.__dict__,'ARCHIVE':ARCHIVE}
    exec(compile(raw,'<actual current boot graph inventory>','exec'),namespace)
    return namespace['validate_actual_graph'](target,hashes)


def main():
    namespace={**prior.prior.engine.__dict__,'__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,
               'TOOLS':TOOLS,'CURRENT':CURRENT,'PRODUCTION':production(),'BEFORE':BEFORE,
               'sources':sources,'validate_actual_graph':validate_actual_graph,'inventory':prior.prior.inventory}
    namespace['write']=types.FunctionType(prior.prior.write.__code__,{**prior.prior.__dict__,'TARGET':TARGET})
    exec(compile(compiler(),'<new actual current boot ABI>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
