from datetime import datetime, date
import os
import praw

no_flair_token = "___NOFLAIR___"

def fix_no_flair(submissions):
    for i in range(len(submissions)):
        if submissions[i].link_flair_text == None:
            submissions[i].link_flair_text = no_flair_token
    return submissions


def get_all_flairs(submissions):
    flairs = []
    for submission in submissions:
        if (
            submission.link_flair_text not in flairs
            and submission.link_flair_text != no_flair_token
        ):
            flairs.append(submission.link_flair_text)
    flairs.sort()
    return flairs


def generate_post_submissions_by_flair(post, submissions, flairs):
    for flair in flairs:
        post = post + "**{}**\n".format(flair)
        for submission in submissions:
            if submission.link_flair_text == flair:
                post = post + "- [{}]({})\n".format(submission.title, submission.url)
        post = post + "\n"
    return post


def add_no_flair_posts(post, submissions, flair):
    post = post + "**Posts Without Flairs**\n"
    for submission in submissions:
        if submission.link_flair_text == no_flair_token:
            post = post + "- [{}]({})\n".format(submission.title, submission.url)
    return post


def submissions_from_last_week(reddit):
    seven_days_ago_utc = datetime.now().timestamp() - 7 * 24 * 60 * 60
    submissions = []
    for submission in reddit.subreddit("AlgorandOfficial").new(limit=100):
        if submission.created_utc >= seven_days_ago_utc:
            submissions.append(submission)
        else:
            break
    submissions = fix_no_flair(submissions)
    return submissions


def get_introductory_post():
    post = "# WEEKLY RECAP"
    post = (
        post
        + "Welcome to the weekly AlgorandOfficial megathread. Here you can find a recap last week's posts, grouped by flair. Enjoy!\n"
    )
    return post


def generate_megathread(reddit):
    submissions = submissions_from_last_week(reddit)
    post = get_introductory_post()
    flairs = get_all_flairs(submissions)
    submissions.sort(key=lambda x: x.link_flair_text)
    post = generate_post_submissions_by_flair(post, submissions, flairs)
    post = add_no_flair_posts(post, submissions, no_flair_token)

    return post

def write_post(post):
    with open("post.md", "w") as f:
        f.write(post)

def post_post(r, post):
    ao = r.subreddit("AlgorandOfficial")
    choices = list(ao.flair.link_templates.user_selectable())
    template_id = next(x for x in choices if x["flair_text"] == "News/Media")["flair_template_id"]
    title = "[MEGATHREAD] WEEKLY RECAP #{} {}".format(datetime.now().isocalendar()[1] - 1, date.today().year)
    ao.submit(
        title=title,
        flair_id=template_id,
        selftext = post,
        send_replies=False,
    )

if __name__ == "__main__":
    reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],  # Client Id
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],  # Client Secret
            user_agent=os.environ["REDDIT_USER_AGENT"],  # User Agent
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
        )
    print("user.me:",   reddit.user.me())
    post = generate_megathread(reddit)
    write_post(post)
    post_post(reddit, post)
