"""Independent174/21 and all36 actual current classes, same single exec with no exclusions."""
import pg7980_exact_duration_post as previous
import pg8006_exact_duration_host_v3 as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG8006-exact-duration-host-v3'
    post.OUT=post.host.BASE/'PG8008-exact-duration-post-v3'
    post.PRIVATE=post.host.W/'pg8008-exact-duration-post-v3'
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
