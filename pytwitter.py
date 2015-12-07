import tweepy, argparse, config

oauthkey = config.oauthkey
oauthsec = config.oauthsec
tokenkey = config.tokenkey
tokensec = config.tokensec

auth = tweepy.OAuthHandler(oauthkey, oauthsec)
auth.set_access_token(tokenkey, tokensec)
api = tweepy.API(auth, wait_on_rate_limit_notify=True)

def limit_handled(cursor):
  while True:
    try:
      yield cursor.next()
    except tweepy.RateLimitError:
      print "Rate limit error."
      time.sleep(2 * 60)

def deleteall():
  for idx, tweet in enumerate(limit_handled(
    tweepy.Cursor(api.user_timeline, max_id=604781336348499969).
    items(3200))):
    print str(idx+1) + " iter"
    print "--- Accessing tweet: " + tweet.text
    print "--- Date posted: " + str(tweet.created_at)
    print "--- Tweet has id: " + tweet.id_str
    try:
      api.destroy_status(int(tweet.id_str))
      print "Deleted tweet."
    except Exception as e:
      print "Tweet with id %s failed with %s" % (tweet.id_str, e)

def main():
  parser = argparse.ArgumentParser(prog="pytwitter",
    description="""delete all your tweets, ever.
    use -r if you'veposted less than 3,200 tweets.
    otherwise specify exact dates with -a.""",
    epilog="2015, @apas",
    formatter_class=argparse.RawTextHelpFormatter)

  group = parser.add_mutually_exclusive_group()
  group.add_argument("-r",
    action="store_true",
    help="delete all tweets (up to 3,200)")
  group.add_argument("-a",
    action="store",
    help="""delete all tweets within a timeframe:\t
    enter timeframe in format YYYY-MM-DD.\t
    the first argument is the older date.\t
    you want the first date to be the day\t
    you created your account and the second,\t
    the current one.""",
    dest="timeframe",
    metavar="timeframe",
    nargs=2)

  args = parser.parse_args()

  if args.r:
    deleteall()
  elif args.timeframe:
    print "todo"
  else:
    parser.print_help()


if __name__ == '__main__':
  main()
