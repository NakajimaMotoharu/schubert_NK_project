"""Public fixed UUID fixture and exact pure-Protocol launcher only; held paths excluded."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'c907c122d'
    stage.PREFIXES += ('tools/quality/pg107','tools/quality/architecture/ProtocolLocaleNegativeJunitLauncher.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10734-protocol-fixture-source-public-delta-v1'
    stage.main()
