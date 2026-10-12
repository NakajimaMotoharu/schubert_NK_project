"""Current ordinary native eight plus unchanged qualified host1532; no Root replay."""
import pg1590_current_native_qualification_v2 as prior

def source():
    raw=prior.source().replace('pg1588-current-native-catalog-v3','pg1614-current-ordinary-native-catalog-v1').replace('pg1590-current-native-qualified-v2','pg1615-current-ordinary-native-qualified-v1').replace('PG1590','PG1615')
    compile(raw,'<ordinary sameSource native qualification transport>','exec');return raw

def main():
    env={**prior.prior.__dict__,'CODE':prior.prior.CODE.replace('PG1587','PG1615')}
    exec(compile(source(),'<ordinary sameSource native analysis>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
