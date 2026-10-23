"""Changed public source/tool/evidence only, no original production PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ad789fd86'
    scan.OUT=scan.scan.BASE/'PG7446-web-generated-public-delta-v1'
    scan.main()
