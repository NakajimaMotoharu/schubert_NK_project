"""Bound public whole8 probe/provider result delta; no product actions or global scan claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13688-mq-provider-public-v1'
scan.BEFORE = 'f0b5385a110ef7c587571ad6da74598ace5f9611'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg136','tools/quality/architecture/MqProviderCurrentEightJunitLauncher.java')

if __name__ == '__main__':scan.main()
