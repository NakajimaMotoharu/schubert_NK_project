"""Current public Grafana candidate data and evidence only, not live config."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='0ad037e111dc88ec4661e6ea76b10e5794045b1e'
    scan.OUT=scan.scan.BASE/'PG8158-grafana-config-public-delta-v1'
    scan.main()
