"""Current HTTP boundary public quality delta only, not complete451 secret gate."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='3146f99da02df8027abdc535dfe009ef18f534fd'
    scan.OUT=scan.scan.BASE/'PG8770-metric-http-fixed-public-delta-v1'
    scan.main()
