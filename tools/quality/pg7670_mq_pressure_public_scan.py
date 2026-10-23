"""Changed own public text/three secret formats only, no runtime or private inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='6315b27f5cd6569ed2f7e5d29b5321d024f17ed5'
    scan.OUT=scan.scan.BASE/'PG7670-mq-pressure-public-delta-v1'
    scan.main()
