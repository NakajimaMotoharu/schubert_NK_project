"""New policy->alert->status original4 independent metadata and real single-session proof."""
from pathlib import Path
import host_connection_metadata_post as audit
import pg8660_policy_alert_status_host as original

if __name__ == '__main__':
    host=audit.post.host
    expected={('dev.codex.schubert.nk.batch.monitoring.PolicyAlertStatusConnectionTest',name) for name in ('alertpipe001AllTwelveThresholdsReachFixedCanonicalStatus','alertpipe002WarningCountAndFiveMinuteRecoveryReachStatus','alertpipe003CriticalRequiresCauseAndInvestigationsStayOpen','alertpipe004MissingBreaksRecoveryAndUtcCannotAccelerateClosure')}
    audit.execute(Path(__file__),original,host.W/'pg8660-policy-alert-status-host-v1',host.W/'pg8662-policy-alert-status-post-v1',host.BASE/'PG8662-policy-alert-status-post-v1','c5f2bfc2134e3b56b0251b36e1f2f5147266efecfcfeb25e76f7887154a26866','PG8660-POLICY-ALERT-STATUS',expected)
