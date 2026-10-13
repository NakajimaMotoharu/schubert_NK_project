"""Same full3633/currentMain native qualification, corrected ownership receipt."""
import pg2256_newboot_native_qualification as prior


def main():
    raw=prior.source().replace('pg2254-newboot-native-catalog-v1','pg2282-current-signed-native-catalog-v1').replace('pg2256-newboot-native-qualified-v1','pg2284-current-signed-native-qualified-v1').replace('PG2256','PG2284')
    engine=prior.prior.prior.engine
    ns={**engine.previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':prior.server().replace('PG2256','PG2284'),'SOURCE':prior.SOURCE,'qualify_snapshot':prior.qualify_snapshot}
    exec(compile(raw,'<corrected native full3633 qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
