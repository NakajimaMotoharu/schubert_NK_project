"""Independent current174/21 full actual36 counters/static, preserving initial failures."""
import pg7980_exact_duration_post as previous
import pg7990_exact_duration_host_v2 as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7990-exact-duration-host-v2'
    post.OUT=post.host.BASE/'PG7992-exact-duration-post-v2'
    post.PRIVATE=post.host.W/'pg7992-exact-duration-post-v2'
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
