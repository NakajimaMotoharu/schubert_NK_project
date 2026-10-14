"""Actual new source ten points/latest nine; preserve old28 without importing."""
import inspect
import pg2562_strict_current_native_catalog as previous
from pg2708_operation_owned_sources import SOURCE,TOOLS,bind
from pg2698_operation_admission_before import before

SLOT='pg2718-operation-native-catalog-v1'


def catalog_source(receipt,binding,end):
    raw=previous.catalog_source(receipt,binding,end)
    for a,b in [(previous.BEFORE,before()),('pg2540-strict-current-noargs-once-v1','pg2684-operation-current-noargs-once-v1'),
      ('require(len(old)==22)','require(len(old)==28)'),('priorOldSourceTwentyTwoCopiesPreserved','priorOldSourceTwentyEightCopiesPreserved')]:raw=raw.replace(a,b)
    return bind(raw)


def main():
    raw=bind(inspect.getsource(previous.main))
    raw=raw.replace('pg2560-strict-current-owned-post-v1','pg2716-operation-owned-post-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':catalog_source}
    exec(compile(raw,'<actual new current native point catalog>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
