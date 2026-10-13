"""New native qualification slot joins current2046 catalog without rewriting receipt negative vectors."""
import pg2044_fresh_normal_warning_native_qualification as prior


def source():
    raw=prior.source().replace('pg2042-fresh-normal-warning-native-catalog-v1','pg2046-receipt-preserving-current-native-catalog-v1').replace('pg2044-fresh-normal-warning-native-qualified-v1','pg2048-receipt-preserving-native-qualified-v1').replace('PG2044','PG2048')
    compile(raw,'<current immutable receipt preserving qualification>','exec');return raw


def main():
    ns={**prior.previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':prior.server().replace('PG2044','PG2048'),'SOURCE':prior.SOURCE,'qualify_snapshot':prior.qualify_snapshot}
    exec(compile(source(),'<current ten point native crc/session qualifier>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
