"""Only new04bb physical points; all72 prior streams remain immutable data only."""
import inspect
import types
import pg4780_new_current_native_catalog as previous
import pg4916_current_owned_sources as role

SLOT='pg4924-current-native-catalog-v1'
BOOT=previous.BOOT
ADMISSION=previous.ADMISSION.replace('==64','==72')


def catalog_source(receipt,binding,end):
    raw=inspect.getsource(previous.previous.catalog_source).replace("'pg4652'","'pg4916'").replace('all58BeforeCopiesPreserved','all72BeforeCopiesPreserved')
    ns={**vars(previous.previous),'role':role,'ADMISSION':ADMISSION,'BOOT':BOOT}
    exec(compile(raw,'<current04bb full11/all72 archive preservation>','exec'),ns)
    return ns['catalog_source'](receipt,binding,end)


def prerequisites(post,terminal):return types.FunctionType(previous.previous.prerequisites.__code__,{**vars(previous.previous),'role':role})(post,terminal)


def main():
    raw=inspect.getsource(previous.previous.main).replace('pg4658-current-owned-post-v1','pg4922-current-owned-post-v1').replace('pg4652_parent_receipt.py','pg4916_parent_receipt.py')
    ns={**vars(previous.previous),'SLOT':SLOT,'role':role,'catalog_source':catalog_source,'prerequisites':prerequisites}
    exec(compile(raw,'<current04bb same-source native catalog>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
