"""BUG1202: bind catalog positive literals before prefixing independent receipt unchanged."""
import inspect
import pg2042_fresh_normal_warning_native_catalog as prior

SLOT='pg2046-receipt-preserving-current-native-catalog-v1'


def catalog_source(receipt):
    raw=inspect.getsource(prior.catalog_source).replace('raw=previous(receipt)','raw=previous(\'\')')
    marker="    from pyflakes.api import check"
    if raw.count(marker)!=1:raise ValueError('one full catalog composition boundary required')
    raw=raw.replace(marker,"    raw=receipt+'\\n'+raw\n"+marker)
    ns={**prior.__dict__,'catalog_source':catalog_source}
    exec(compile(raw,'<body-only positive binding, unchanged receipt>','exec'),ns);result=ns['catalog_source'](receipt)
    if not result.startswith(receipt+'\n'):raise ValueError('independent receipt bytes must not change')
    return result


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'catalog_source':catalog_source}
    exec(compile(inspect.getsource(prior.main),'<new native catalog slot unchanged receipt>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
