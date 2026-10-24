"""Ownership correction public delta only, not full451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='a370c32ea14a1a9104dda8e178114f326a72e038'
    scan.OUT=scan.scan.BASE/'PG8962-canonical-owner-public-delta-v1'
    scan.main()
