"""New-only current bytes-schema catalog / same-qualified-source native union."""
import pg1615_current_ordinary_native_qualification as prior

def source():
    return prior.source().replace('pg1614-current-ordinary-native-catalog-v1','pg1616-current-ordinary-native-catalog-v2').replace('pg1615-current-ordinary-native-qualified-v1','pg1617-current-ordinary-native-qualified-v2').replace('PG1615','PG1617')

def main():
    env={**prior.prior.prior.__dict__,'CODE':prior.prior.prior.CODE.replace('PG1587','PG1617')}
    exec(compile(source(),'<current strict sameSource native analysis>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
