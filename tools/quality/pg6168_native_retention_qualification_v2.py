"""Independent original25 XML/sixJars/all8511667/static; not real native Root qualification."""
from pg5940_private_lock_compile import W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6162_native_ports_static import MAIN
from pg6164_native_retention_selected import inventory

SOURCE='423f329ce7dcdbd339669018f1e10ad23dc1b8d3'


def main():
    cases,_=inventory()
    return qualify(SOURCE,W/'pg6166-native-retention-selected-v2',cases,(25,13),MAIN,
        BASE/'PG6132-api-management-stop-qualification-v1/manifest.json',
        'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d',
        W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json',
        W/'pg6132-api-management-stop-qualification-v1/findings.safe.json',
        'pg6168-native-retention-qualification-v2','PG6168-native-retention-qualification-v2')


if __name__=='__main__':main()
