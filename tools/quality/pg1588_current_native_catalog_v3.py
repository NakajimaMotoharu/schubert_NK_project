"""Static-clean new-only catalog; preserve old generated source and results."""
import inspect
import pg1586_current_native_catalog_v2 as prior

def catalog_source():
    raw=prior.catalog_source();old='import hashlib,json,os,pathlib,stat'
    if raw.count(old)!=1:raise ValueError('one unused generated import required')
    return raw.replace(old,'import hashlib,json,pathlib,stat')

def main():
    raw=inspect.getsource(prior.prior.main).replace('pg1584-current-native-catalog-v1','pg1588-current-native-catalog-v3')
    env={**prior.prior.__dict__,'CODE':catalog_source()};exec(compile(raw,'<new static clean catalog>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
