"""Same original15 cases/source and exact SDK pins after owned-fixture correction."""
import pg7108_micrometer_http_post as original
import pg7110_micrometer_http_host_v2 as host


if __name__=='__main__':
    post=original.configure()
    post.SLOT=host.SLOT
    post.RUN='PG7110-micrometer-http-host-v2'
    post.OUT=post.host.BASE/'PG7112-micrometer-http-post-v2'
    post.PRIVATE=post.host.W/'pg7112-micrometer-http-post-v2'
    post.main()
