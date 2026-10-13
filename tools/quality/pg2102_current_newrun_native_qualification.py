"""Same current Main/full3618 bytes plus actual newrun ten native points, no historical exec imports."""
import inspect
import pg2048_receipt_preserving_native_qualification as previous


def source():
    raw=previous.source().replace('pg2046-receipt-preserving-current-native-catalog-v1','pg2100-current-newrun-native-catalog-v1').replace('pg2048-receipt-preserving-native-qualified-v1','pg2102-current-newrun-native-qualified-v1').replace('PG2048','PG2102')
    compile(raw,'<actual current newrun native qualification transport>','exec');return raw


def main():
    raw=inspect.getsource(previous.main)
    ns={**previous.__dict__,'source':source}
    exec(compile(raw,'<actual current newrun byte/session qualifier>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
