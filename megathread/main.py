from datetime import datetime, date, timedelta
import os
import praw

no_flair_token = "___NOFLAIR___"
min_score = 5

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
            if submission.link_flair_text == flair and submission.score > min_score and "airdrop" not in submission.title:
                post = post + get_submission_markup(submission)
        post = post + "\n"

    post = post + "**Posts Without Flairs**\n"
    for submission in submissions:
        if submission.link_flair_text == no_flair_token and submission.score > min_score:
            post = post + get_submission_markup(submission)
    return post

def sort_submissions(submissions):
    return sorted(submissions, key=lambda x: x.score, reverse=True)
    
def get_submission_markup(submission):
    return "- [{}]({}) | S: {}, R: {}, C: {}\n".format(submission.title, submission.permalink, submission.score, submission.upvote_ratio, submission.num_comments)

def submissions_from_last_week(reddit):
    seven_days_ago_utc = datetime.now().timestamp() - 7 * 24 * 60 * 60
    submissions = []
    for submission in reddit.subreddit("AlgorandOfficial").new(limit=200):
        if submission.created_utc >= seven_days_ago_utc:
            submissions.append(submission)
        else:
            break
    submissions = fix_no_flair(submissions)
    return submissions


def get_introductory_post():
    post = "Welcome to the weekly AlgorandOfficial subreddit recap megathread. Here you can find a recap of last week's posts, with a minimum score of {} and grouped by flair and sorted by score. S = Score, R = Ratio, C = Comments. Enjoy!\n\n\n".format(min_score)
    return post

def generate_megathread(reddit):
    submissions = submissions_from_last_week(reddit)
    sorted_submissions = sort_submissions(submissions)
    post = get_introductory_post()
    flairs = get_all_flairs(sorted_submissions)
    post = generate_post_submissions_by_flair(post, sorted_submissions, flairs)
    return post

def write_post(post):
    with open("post.md", "w") as f:
        f.write(post)

def post_post(r, post):
    ao = r.subreddit("AlgorandOfficial")
    choices = list(ao.flair.link_templates.user_selectable())
    template_id = next(x for x in choices if x["flair_text"] == "Megathread")["flair_template_id"]
    d = "{} - {} {}".format(
        (date.today() - timedelta(days=7)).strftime('%b %d'), 
        date.today().strftime('%b %d'), 
        date.today().year)
    title = "r/AlgorandOfficial Weekly Recap: {}".format(d)
    ao.submit(
        title=title,
        flair_id=template_id,
        selftext = post,
        send_replies=False,
    )

if __name__ == "__main__":
    reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
        )
    post = generate_megathread(reddit)
    write_post(post)
    post_post(reddit, post)
