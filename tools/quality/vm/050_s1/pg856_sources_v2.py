"""BUG972 new-only import-complete generated recovery; immutable v1 partial retained."""
import pg856_sources as old
SOURCE=old.SOURCE;DIGEST=old.DIGEST;SNAPSHOT=old.SNAPSHOT;EPOCH=old.EPOCH
def bind(raw):
    return old.bind(raw).replace('pg856-failed-done-tools-v1','pg856-failed-done-tools-v2').replace('pg856-failed-done-recovery-v1','pg856-failed-done-recovery-v2').replace('pg856-frozen-v2','pg856-frozen-v3').replace('pg856-database-oracle-v1','pg856-database-oracle-v2').replace('pg856-oracle-v2','pg856-oracle-v3').replace("'-v2.private.log'","'-v3.private.log'").replace("'-v2.exit'","'-v3.exit'").replace("action+'-v2'","action+'-v3'").replace('pg856-stage-v2','pg856-stage-v3').replace('pg856-verify-v2','pg856-verify-v3').replace('pg856-fixed-stage-v2','pg856-fixed-stage-v3')
def java():
    raw=old.java();marker='import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;'
    assert raw.count(marker)==1
    return bind(raw.replace(marker,marker+'\nimport dev.codex.schubert.nk.batch.repository.MaintenanceActivation;'))
def helper():return bind(old.helper())
def java_test():return old.java_test()
