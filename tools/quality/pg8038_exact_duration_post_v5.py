"""Recover unchanged174 original exec with explicit zero-code metadata contract; no PT replay."""
import pg8024_exact_duration_post_v4 as previous
def configure():
    post=previous.configure()
    post.OUT=post.host.BASE/'PG8038-exact-duration-post-v5'
    post.PRIVATE=post.host.W/'pg8038-exact-duration-post-v5'
    return post
if __name__=='__main__':
    previous.host.dependency.verify_inputs()
    configure().main()
