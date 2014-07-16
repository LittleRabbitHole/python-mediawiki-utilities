import sys,os;sys.path.insert(0, os.path.abspath(os.getcwd()))
from mw.api import Session
from mw.lib import sessions

# Gather a user's revisions from the API
api_session = Session("https://en.wikipedia.org/w/api.php")
revs = api_session.user_contribs.query(
    user={"TestAccountForMWUtils"},
    direction="newer"
)
rev_events = ((rev['user'], rev['timestamp'], rev) for rev in revs)

# Extract and print sessions
for user, session in sessions.cluster(rev_events):
    print("{0}'s session with {1} revisions".format(user, len(session)))
