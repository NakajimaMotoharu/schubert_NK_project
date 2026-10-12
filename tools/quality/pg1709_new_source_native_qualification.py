"""Qualified current2741 native/CRC union with3596 host; never oldSource exec."""
import pg1618_current_ordinary_native_qualification_v3 as prior
from pg1700_new_source_live_binding import SOURCE


def source():
    raw=prior.source()
    for old,new in [('pg1616-current-ordinary-native-catalog-v2','pg1708-new-source-native-catalog-v1'),
                    ('pg1618-current-ordinary-native-qualified-v3','pg1709-new-source-native-qualified-v1'),
                    ('PG1618','PG1709'),('pg1542-filesystem-full-qualified-v3','pg1636-api-boundary-full-qualified-v1')]:
        if old not in raw:raise ValueError('one sameSource catalog/full transport join required')
        raw=raw.replace(old,new)
    check="['git','diff','--name-only',SOURCE,'--','src','pom.xml']"
    if raw.count(check)!=1:raise ValueError('one full qualified test snapshot gate required')
    raw=raw.replace(check,"['git','diff','--name-only','1683dd9f6de00e71d2317d9af3cd50400a37bf4e','--','src','pom.xml']")
    compile(raw,'<new Source eight-native qualification transport>','exec')
    return raw


def server():
    raw=prior.prior.prior.prior.prior.CODE
    for old,new in [('PG1587','PG1709'),('PG1532','PG1633'),('3583','3596'),
                    ('qualified1532Tests','qualified1633Tests'),
                    ('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE)]:
        if old not in raw:raise ValueError('sameSource native host input boundary missing')
        raw=raw.replace(old,new)
    compile(raw,'<new Source independently qualified3596 native union>','exec')
    return raw


def main():
    ns={**prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':SOURCE}
    exec(compile(source(),'<new Source native readonly campaign>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
