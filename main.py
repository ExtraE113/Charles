import time
from collections import namedtuple
from urllib.parse import urlparse
from urllib.parse import urlunparse
from bs4 import BeautifulSoup
import praw
import re
import bitly

# matches amazon links but not other links, only matches links that amazon smile works for
# (doesn't work in canada, china, or japan)
# we could redirect those to smile.amazon.com but I don't want to edit the destination for fear of unexpected behavior
# or language issues
AMAZON_REGIONALS_REGEX = re.compile("(https://|http://)(www\.)?amazon\.(co\.uk|com|de)")
SIGN_OFF = "I'm a bot and this action was performed automatically."
SOOut = ""
for i in SIGN_OFF.split(" "):
	SOOut += "^^^" + i + " "
SIGN_OFF = SOOut
comments = 0
links = 0
amazon_links = 0
reddit_links = 0


def main():
	try:
		reddit = praw.Reddit("bot1", user_agent="Linkbot v0.0.1")

		subreddit = reddit.subreddit("all")
		for submission in subreddit.stream.comments():
			process_submission(submission)
	except BaseException as e:
		print(e)
		time.sleep(60)
		main()


def process_submission(submission):
	# this should never happen, but if we somehow happen across one of our comments just ignore it
	if submission.author.name == "CharitableLinkBot":
		return

	# this gets us the data as html and parses it to an easily-used format
	soup = BeautifulSoup(submission.body_html, 'html.parser')

	# keep track of our metrics
	global comments, links, amazon_links, reddit_links
	comments += 1

	if soup.a is not None:
		# for each link in the comment
		for link in soup.find_all('a'):
			links += 1

			# checks if it's a amazon link
			if AMAZON_REGIONALS_REGEX.match(link.get('href')):
				print(link.get("href"))
				amazon_links += 1

				o = urlparse(link.get('href'))
				# convert the parsed url to a dict so its easier to work on
				# probably not the cleanest but whatever
				o = o._asdict()

				print(o)

				# split the domain into subdomains, so `"www.amazon.com"` becomes `["www", "amazon", "com"]
				domain_parts = o["netloc"].split(".")

				# and rebuild the domain
				if len(domain_parts) >= 3:
					domain_parts[0] = "smile"  # the whole point!
				o["netloc"] = ".".join(domain_parts)

				# https://stackoverflow.com/questions/43921240/pythonic-way-to-convert-a-dictionary-into-namedtuple-or-another-hashable-dict-li
				parser_input = namedtuple('parser_input', o.keys())(**o)
				out = urlunparse(parser_input)

				print(f"Smile'd link: {out}")

				# get a bit.ly link for easy tracking
				# link = bitly.get_short_link(out)  # we can't do this because reddit doesn't like link shorteners :(

				link = out

				# and post the comment
				replymd = "Try amazon smile to donate to a charity of your choice automatically at no cost to you!  "
				replymd += "\n" + f"[{out}]({link})  "
				replymd += "\n" + SOOut
				print(replymd)
				count = 0
				while True:
					try:
						submission.reply(replymd)
						return  # we'll only get here if the previous line succeeded
					except praw.exceptions.RedditAPIException as e:
						count += 1
						if (count > 10):
							count = 0
							return
						print("Waiting, then trying again...." + str(e))
						time.sleep(30)  # wait 30 seconds and then try again
					except BaseException as e:
						print("encountered exception we don't know how to handle. moving on")
						print(e)
						return



			elif "/r/" in link.get('href'):
				reddit_links += 1

	if comments % 1000 == 0:
		print(
			f"{comments} comments processed. {links} links found, {reddit_links} of which were reddit links and "
			f"{amazon_links} were amazon links."
		)


if __name__ == "__main__":
	main()
