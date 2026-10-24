"""New-only BUG1689 resource-corrected selected JUnit; original PG8178 failure preserved."""
import pg8178_web_prometheus_gauge_host as run

if __name__=='__main__':
    run.SLOT=run.host.W/'pg8182-web-prometheus-gauge-host-v1'
    run.OUT=run.host.BASE/'PG8182-web-prometheus-gauge-host-v1'
    run.SESSION_ID='PG8182-WEB-PROMETHEUS-GAUGE'
    run.main()
