"""Only new0ea physical points; prior94 streams preserved as data, never credited."""
import inspect
import types
import pg5508_current_native_catalog as previous
import pg5670_current_owned_sources as role

SLOT='pg5680-current-native-catalog-v1'
BOOT=previous.BOOT
ADMISSION=previous.ADMISSION.replace('==88','==94')
TEMPLATE=previous.TEMPLATE


def catalog_source(receipt,binding,end):
    raw=inspect.getsource(TEMPLATE.catalog_source).replace("'pg4652'","'pg5670'")
    raw=raw.replace('all58BeforeCopiesPreserved','all94BeforeCopiesPreserved')
    ns={**vars(TEMPLATE),'role':role,'ADMISSION':ADMISSION,'BOOT':BOOT}
    exec(compile(raw,'<same0ea all94 oldphysicalcopies preserved>','exec'),ns)
    return ns['catalog_source'](receipt,binding,end)


def prerequisites(post,terminal):
    if type(post.get('actualExit'))is not int:raise ValueError('actual numeric fullstop post first')
    return types.FunctionType(TEMPLATE.prerequisites.__code__,{**vars(TEMPLATE),'role':role})(post,terminal)


def main():
    raw=inspect.getsource(TEMPLATE.main).replace('pg4658-current-owned-post-v1','pg5676-current-owned-post-v1')
    raw=raw.replace('pg4652_parent_receipt.py','pg5670_parent_receipt.py')
    ns={**vars(TEMPLATE),'SLOT':SLOT,'role':role,'catalog_source':catalog_source,'prerequisites':prerequisites}
    exec(compile(raw,'<same0ea sourceonly catalog after genuine5674stop>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
