"""Independent174/21/43Java/36actual plus2 proved metadata, no counter exclusions."""
import pg7980_exact_duration_post as previous
import pg8022_exact_duration_host_v4 as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG8022-exact-duration-host-v4'
    post.OUT=post.host.BASE/'PG8024-exact-duration-post-v4'
    post.PRIVATE=post.host.W/'pg8024-exact-duration-post-v4'
    post.SOURCE_FILE_COUNT=43
    post.EXTRA_MARKER_METADATA={post.PREFIX+'ExactDurationSupport.class':
        '1723/BUG1679 package-local factory capability; no fields/methods/initialization; retained physical only'}
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
