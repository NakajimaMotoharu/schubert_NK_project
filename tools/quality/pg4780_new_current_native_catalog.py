"""New source native point catalog, original64 streams are immutable data only."""
import inspect
import types
import pg4660_current_native_catalog as previous
import pg4772_new_current_owned_sources as role

SLOT='pg4780-new-current-native-catalog-v1'
BOOT=previous.BOOT
ADMISSION=previous.ADMISSION.replace("{'units','actors','database','flocks','durable','native','startup','runtime','configuration'}","{'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native'}").replace("frozen['database']['rows']","frozen['rows']").replace('==58','==64')


def catalog_source(receipt,binding,end):
    raw=inspect.getsource(previous.catalog_source).replace("'pg4652'","'pg4772'").replace('all58BeforeCopiesPreserved','all64BeforeCopiesPreserved')
    ns={**vars(previous),'role':role,'ADMISSION':ADMISSION,'BOOT':BOOT}
    exec(compile(raw,'<new full11 current native source factory>','exec'),ns)
    return ns['catalog_source'](receipt,binding,end)


def prerequisites(post,terminal):return types.FunctionType(previous.prerequisites.__code__,{**vars(previous),'role':role})(post,terminal)


def main():
    raw=inspect.getsource(previous.main).replace('pg4658-current-owned-post-v1','pg4778-new-current-owned-post-v1').replace('pg4652_parent_receipt.py','pg4772_parent_receipt.py')
    ns={**vars(previous),'SLOT':SLOT,'role':role,'catalog_source':catalog_source,'prerequisites':prerequisites}
    exec(compile(raw,'<new same-source catalog owner-preserving entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
