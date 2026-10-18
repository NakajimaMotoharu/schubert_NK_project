"""Only new a2ecc physical points; all80 prior streams preserved as data only."""
import inspect
import types
import pg4924_current_native_catalog as previous
import pg5060_current_owned_sources as role

SLOT = 'pg5070-current-native-catalog-v1'
BOOT = previous.BOOT
ADMISSION = previous.ADMISSION.replace('==72', '==80')
TEMPLATE = previous.previous.previous


def catalog_source(receipt, binding, end):
    raw = inspect.getsource(TEMPLATE.catalog_source).replace("'pg4652'", "'pg5060'")
    raw = raw.replace('all58BeforeCopiesPreserved', 'all80BeforeCopiesPreserved')
    ns = {**vars(TEMPLATE), 'role': role, 'ADMISSION': ADMISSION, 'BOOT': BOOT}
    exec(compile(raw, '<currenta2ecc full11/all80 archive preservation>', 'exec'), ns)
    return ns['catalog_source'](receipt, binding, end)


def prerequisites(post, terminal):
    if type(post.get('actualExit')) is not int:
        raise ValueError('actual numeric full stop post first')
    return types.FunctionType(TEMPLATE.prerequisites.__code__, {**vars(TEMPLATE), 'role': role})(post, terminal)


def main():
    raw = inspect.getsource(TEMPLATE.main).replace('pg4658-current-owned-post-v1', 'pg5066-current-owned-post-v1')
    raw = raw.replace('pg4652_parent_receipt.py', 'pg5060_parent_receipt.py')
    ns = {**vars(TEMPLATE), 'SLOT': SLOT, 'role': role,
          'catalog_source': catalog_source, 'prerequisites': prerequisites}
    exec(compile(raw, '<a2ecc current same-source native catalog>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
