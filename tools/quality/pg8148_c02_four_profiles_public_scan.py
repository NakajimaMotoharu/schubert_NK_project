"""C02 public declarations and independent oracle delta; no runtime inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='0d90f7838b18882c057f4ab5f5429f25f1e20380'
    scan.OUT=scan.scan.BASE/'PG8148-c02-four-profiles-public-delta-v1'
    scan.main()
