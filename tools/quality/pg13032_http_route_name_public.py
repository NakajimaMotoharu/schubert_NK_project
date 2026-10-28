"""Final explicit public source/evidence/document delta; held paths excluded before content."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13032-http-route-name-public-v1'
    scan.BEFORE = '507cf94c0ba3dfe5e2fec3ac093bbd83843e5047'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130','tools/quality/architecture/HttpRouteNameJunitLauncher.java','tools/quality/architecture/HttpRouteNameArtifactCoverageMeasure.java')
    scan.main()
