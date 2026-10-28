"""Final public delta only; existing held two are removed before any content read."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13010-value-binding-public-v1'
    scan.BEFORE = '530fc666e41ca251a7a37d9e561144b3b4fef719'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129','tools/quality/pg130','tools/quality/architecture/ValueBindingJunitLauncher.java','tools/quality/architecture/ValueBindingArtifactCoverageMeasure.java')
    scan.main()
