"""New-only corrected role-qualified physical trace, original preflight failure preserved."""
import pg8218_counter_name_six_trace as trace

if __name__=='__main__':
    trace.SLOT=trace.host.W/'pg8219-counter-name-six-trace-v2'
    trace.OUT=trace.host.BASE/'PG8219-counter-name-six-trace-v2'
    trace.main()
