# encoding=utf8
import tweepy, argparse, config, subprocess, time, datetime, glob, os, csv
from datetime import date
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
    tweepy.Cursor(api.user_timeline).items(3200))):
    print str(idx+1) + " iter"
    print "--- Accessing tweet: " + tweet.text
    print "--- Date posted: " + str(tweet.created_at)
    print "--- Tweet has id: " + tweet.id_str
    try:
      api.destroy_status(int(tweet.id_str))
      print "Deleted tweet."
    except Exception as e:
      print "Tweet with id %s failed with %s" % (tweet.id_str, e)

def rm(filename):
  outputcsvs = glob.glob(filename)
  for cvsfile in outputcsvs:
    os.remove(cvsfile)

def timeframe(date):
  username = date[0]
  s_date = date[1]
  e_date = date[2]
  u = "username="+username

  start_date = datetime.datetime.strptime(s_date, "%Y-%m-%d").date()
  end_date = datetime.datetime.strptime(e_date, "%Y-%m-%d").date()

  cnt = 1
  thirtydaysinterval = datetime.timedelta(days=30)
  delta = end_date - start_date
  temp_start_date = start_date

  while delta.days > 30:
    temp_until_date = temp_start_date + thirtydaysinterval
    cmdsince = "since="+str(temp_start_date)
    cmduntil = "until="+str(temp_until_date)
    create_csv = subprocess.call(["java", "-jar", "got.jar",
     u, cmdsince, cmduntil])
    newname = "output_got-%s.csv" % str(cnt)
    rename = subprocess.call(["mv", "output_got.csv", newname])
    temp_start_date = temp_until_date
    delta = end_date - temp_start_date
    cnt += 1
    print temp_start_date
    print temp_until_date
    print "# END ITER"
  else:
    cmdsince = "since="+str(temp_start_date)
    cmduntil = "until="+str(end_date)
    create_csv = subprocess.call(["java", "-jar", "got.jar",
     u, cmdsince, cmduntil])
    newname = "output_got-%s.csv" % str(cnt)
    rename = subprocess.call(["mv", "output_got.csv", newname])
    print temp_start_date
    print end_date
    print "# END ITER"

  # eventually check here if merged.csv already exists and, if Y, rm it
  merge = subprocess.call(["./merge.sh"])
  rm("output_got-*")
  print "All CSVs merged."

  idlist = []
  with codecs.open('merged.csv', 'rb', encoding='utf-8') as f:
    data = csv.reader(f, delimiter=';', quotechar='"')
    for row in data:
      try:
        if row[-2] != "id":
          print row[-2]
          idlist.append(row[-2])
      except IndexError:
        pass
      except Exception as e:
        rm("merged.csv")
        raise e

  for idx, status in enumerate(idlist):
    try:
      api.destroy_status(int(status))
      print "Deleted tweet: " + status
    except Exception as e:
      rm("merged.csv")
      raise e

    rm("merged.csv")

def main():
  parser = argparse.ArgumentParser(prog="pytwitter",
    description="""delete all your tweets, ever.
    use -r if you've posted less than 3,200 tweets.
    otherwise specify your username and the exact
    dates with -a.""",
    epilog="2015, @apas",
    formatter_class=argparse.RawTextHelpFormatter)

  group = parser.add_mutually_exclusive_group()
  group.add_argument("-r",
    action="store_true",
    help="delete all tweets (up to 3,200)")
  group.add_argument("-a",
    action="store",
    help="""delete all tweets within a timeframe:\t
    enter timeframe like: username YYYY-MM-DD YYYY-MM-DD.\t
    the first date argument is the older date.\t
    (you want the first date to be the day\t
    you created your account and the second,\t
    the current one.)""",
    dest="timeframe",
    metavar="timeframe",
    nargs=3)

  args = parser.parse_args()

  if args.r:
    deleteall()
  elif args.timeframe:
    timeframe(args.timeframe)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()
