"""Current public configuration delta only; no live or private inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='31dfdb91ab0072ff0c7ce42b7f195d2b79d6b6fb'
    scan.OUT=scan.scan.BASE/'PG8142-prometheus-config-public-delta-v1'
    scan.main()
