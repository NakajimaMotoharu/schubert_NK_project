"""Public current four XML component cases, independent post, and preserved prebody lint."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13868-broker-config-public-v1'
scan.BEFORE = 'cff2f978c49c2c598b6a75cc448d5870a9f71d64'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/BrokerPublicConfigurationCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
