"""Only the original completed15 v3 cases, actual SDK and current physical classes."""
import pg7108_micrometer_http_post as original
import pg7116_micrometer_http_host_v3 as host


if __name__=='__main__':
    post=original.configure()
    post.SLOT=host.SLOT
    post.RUN='PG7116-micrometer-http-host-v3'
    post.OUT=post.host.BASE/'PG7118-micrometer-http-post-v3'
    post.PRIVATE=post.host.W/'pg7118-micrometer-http-post-v3'
    post.main()
