"""Same161/40 actual classes for fixed source; original31-row qualification never overwritten."""
import pg7268_transfer_metric_post as previous
import pg7272_transfer_metric_host_v2 as host

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7272-transfer-metric-host-v2'
    post.OUT=post.host.BASE/'PG7274-transfer-metric-post-v2'
    post.PRIVATE=post.host.W/'pg7274-transfer-metric-post-v2'
    post.main()
