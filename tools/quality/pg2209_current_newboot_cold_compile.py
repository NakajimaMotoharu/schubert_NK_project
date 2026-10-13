"""Actual current signed bundle ABI for existing completed-cold ownership protocol."""
import inspect
import pg1442_current_cold_compile as prior
from pg2208_current_newboot_cold_sources import java,observer,qualify_before,TOOLS,SOURCE


def main():
    qualify_before()
    raw=inspect.getsource(prior.main)
    pairs=[('Pg1441CurrentColdPreparation','Pg2208CurrentColdPreparation'),
      ('pg1441_current_cold_refs.py','pg2208_current_cold_refs.py'),
      ('pg1441_current_cold_sources_test.py','pg2208_current_newboot_cold_sources_test.py'),
      ('PG1442-current-cold-compile-v1','PG2209-current-newboot-cold-compile-v1'),
      ('pg1442-current-cold-frozen-v1.safe.json','pg2209-current-newboot-cold-frozen-v1.safe.json'),
      ('pg1292-release-v1','pg2126-release-v1')]
    for old,new in pairs:
        if old not in raw:raise ValueError('exact current compiler role required '+old)
        raw=raw.replace(old,new)
    # Reusable helper byte inputs retain their historical qualification source;
    # emitted current graph receives this production source, never old native.
    old="'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f'"
    if raw.count(old)!=1:raise ValueError('one result source role required')
    raw=raw.replace(old,"'productionSource':SOURCE")
    ns={**prior.__dict__,'OUT':prior.W/TOOLS,'java':java,'observer':observer,'SOURCE':SOURCE}
    exec(compile(raw,'<actual newboot current cold ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
