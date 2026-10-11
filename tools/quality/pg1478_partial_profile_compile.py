"""New source-frozen readonly operator profile against current769 qualified ABI."""
import inspect
import pg1442_current_cold_compile as compiler
from pg1478_partial_original_profile_sources import java,refs


def main():
    entry=inspect.getsource(compiler.main)
    for old,new in [('Pg1441CurrentColdPreparation','Pg1478PartialOriginalProfile'),
                    ('pg1441_current_cold_refs.py','pg1478_partial_original_refs.py'),
                    ('pg1441_current_cold_sources_test.py','pg1478_partial_original_profile_sources_test.py'),
                    ('PG1442-current-cold-compile-v1','PG1478-partial-profile-compile-v1'),
                    ('pg1442-current-cold-frozen-v1.safe.json','pg1478-partial-profile-frozen-v1.safe.json')]:
        if old not in entry:raise ValueError('fixed source compiler insertion refused')
        entry=entry.replace(old,new)
    namespace={**compiler.__dict__,'OUT':compiler.W/'pg1478-partial-original-tools-v1',
               'java':java,'observer':refs}
    exec(compile(entry,'<new readonly partial profile compiler>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
