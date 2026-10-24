"""Public full-overload changed-source quality delta only."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='9997877d1bb84a1fe87d3e915d74436fd1cbd5cf'
    scan.OUT=scan.scan.BASE/'PG8730-full-metric-payload-public-delta-v1'
    scan.main()
