"""Only new296 physical points; all88 prior native streams preserved as data, never credited."""
import inspect
import types
import pg5070_current_native_catalog as previous
import pg5496_current_owned_sources as role

SLOT='pg5508-current-native-catalog-v1'
BOOT=previous.BOOT
ADMISSION=previous.ADMISSION.replace('==80','==88')
TEMPLATE=previous.TEMPLATE


def catalog_source(receipt,binding,end):
    raw=inspect.getsource(TEMPLATE.catalog_source).replace("'pg4652'","'pg5496'")
    raw=raw.replace('all58BeforeCopiesPreserved','all88BeforeCopiesPreserved')
    ns={**vars(TEMPLATE),'role':role,'ADMISSION':ADMISSION,'BOOT':BOOT}
    exec(compile(raw,'<same296 full11/all88 copies preserved>','exec'),ns)
    return ns['catalog_source'](receipt,binding,end)


def prerequisites(post,terminal):
    if type(post.get('actualExit'))is not int:raise ValueError('actual numeric full stop post first')
    return types.FunctionType(TEMPLATE.prerequisites.__code__,{**vars(TEMPLATE),'role':role})(post,terminal)


def main():
    raw=inspect.getsource(TEMPLATE.main).replace('pg4658-current-owned-post-v1','pg5502-current-owned-post-v1')
    raw=raw.replace('pg4652_parent_receipt.py','pg5496_parent_receipt.py')
    ns={**vars(TEMPLATE),'SLOT':SLOT,'role':role,'catalog_source':catalog_source,'prerequisites':prerequisites}
    exec(compile(raw,'<same296 source-only catalog after actual stop>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
