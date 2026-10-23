"""Fixed-source70 qualification; exact actual entrypoint and loaded project tools are bound."""
import pg7066_timed_filesystem_post as original
import pg7068_timed_filesystem_host_v2 as host


if __name__=='__main__':
    post=original.configure()
    post.SLOT=host.SLOT
    post.RUN='PG7068-timed-filesystem-host-v2'
    post.OUT=post.host.BASE/'PG7070-timed-filesystem-post-v2'
    post.PRIVATE=post.host.W/'pg7070-timed-filesystem-post-v2'
    post.main()
