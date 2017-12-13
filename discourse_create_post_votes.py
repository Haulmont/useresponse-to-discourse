# -*- coding: utf-8 -*-

import sys
import time
import config
import subprocess
import psycopg2
import logging
import MySQLdb.cursors
from logging.handlers import RotatingFileHandler
from pydiscourse import DiscourseClient

reload(sys)
sys.setdefaultencoding('utf8')

# Counter
start_global_ts = time.time()

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = RotatingFileHandler('migrate_post_votes.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate POST VOTES.\n')

# ===================================================================
# connect to Discourse
# ===================================================================

logger.info('Connecting to Discourse...')
discourse = DiscourseClient(
    config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER,
    api_username=(config.DISCOURSE_LOGIN),
    api_key=(config.DISCOURSE_API_KEY)
)

# ===================================================================
# connect to mysql
# ===================================================================

logger.info('Connecting to UseResponse (mysql)...')
try:
    useresponse_db = MySQLdb.connect(use_unicode=True, charset='utf8',
                                     host=(config.USERESPONSE_DATABASE_HOST),
                                     port=(config.USERESPONSE_DATABASE_PORT),
                                     user=(config.USERESPONSE_DATABASE_LOGIN),
                                     passwd=(config.USERESPONSE_DATABASE_PASSWORD),
                                     db=(config.USERESPONSE_DATABASE_NAME),
                                     cursorclass=MySQLdb.cursors.DictCursor)
except MySQLdb.Error, e:
    logger.error('Error %d: %s' % (e.args[0], e.args[1]))
    sys.exit(1)

# ===================================================================
# connect to postgres
# ===================================================================

logger.info('Connecting to Discourse (pgsql)...')
# Define our connection string
conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (
    config.DISCOURSE_DATABASE_HOST, config.DISCOURSE_DATABASE_PORT, config.DISCOURSE_DATABASE_NAME,
    config.DISCOURSE_DATABASE_LOGIN,
    config.DISCOURSE_DATABASE_PASSWORD)

# get a connection, if a connect cannot be made an exception will be raised here
conn_pgsql = psycopg2.connect(conn_string)

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cursor_pgsql = conn_pgsql.cursor()

# ===================================================================
# mysql cursors
# ===================================================================

cursor_get_topic_votes_info = useresponse_db.cursor()
cursor_get_post_votes_info = useresponse_db.cursor()
cursor_get_voter_info = useresponse_db.cursor()
cursor_find_matched_topic = useresponse_db.cursor()
cursor_find_matched_post = useresponse_db.cursor()
cursor_find_matched_user = useresponse_db.cursor()
cursor_find_post_author = useresponse_db.cursor()

# POSTS

logger.info('Reading votes for posts...')
query_get_post_votes = """
select v.object_id as 'vote_id',
       v.created_by_id as 'vote_user_id',
       c.id as 'comment_id',
       c.created_by_id as 'comment_user_id',
       v.created_at
from ur_votes v join
     ur_comments c
     on v.object_id = c.id
where v.created_by_id <> c.created_by_id
      and v.value <> 0
      and v.owner like 'comment%'
      order by v.created_at
      """
cursor_get_post_votes_info.execute(query_get_post_votes)

i = 0

post_votes = cursor_get_post_votes_info.fetchmany(250)

while post_votes:

    x = 1

    # iterate votes by id
    for vote in post_votes:
        # time.sleep(0.05)

        startTs = time.time()

        # read vote
        post_vote_object_id = vote['comment_id']
        post_useresponse_user_id = vote['comment_user_id']
        post_vote_by_user = vote['vote_user_id']
        post_vote_date = vote['created_at']

        logger.info('%d/%d. Migrating vote for post ID: %s by user ID: %s on %s' % (
            i, x, post_vote_object_id, post_vote_by_user, post_vote_date))

        # find matched comment and post
        query_find_matched_post = """select discourse_comment_id, discourse_topic_id from match_comments
                                     where useresponse_comment_id = %s;"""
        vars_find_matched_post = post_vote_object_id
        cursor_find_matched_post.execute(query_find_matched_post, (vars_find_matched_post,))
        post = cursor_find_matched_post.fetchone()

        if post:
            post_id = post['discourse_comment_id']
            topic_id = post['discourse_topic_id']

            # find matched post author
            query_find_post_author = "select user_id from posts where id = %s;"
            vars_find_post_author = (post_useresponse_user_id,)
            cursor_pgsql.execute(query_find_post_author, vars_find_post_author)
            post_author = cursor_pgsql.fetchone()

            # find matched post voter
            query_find_voter = "select discourse_id from match_users where useresponse_id = %s;"
            vars_find_voter = post_vote_by_user
            cursor_get_voter_info.execute(query_find_voter, (vars_find_voter,))
            user = cursor_get_voter_info.fetchone()

            try:
                voter = user['discourse_id']
            except Exception, ex:
                logger.error("User not found!" + ex.message, exc_info=True)
                voter = -2

            # post a like using API (post_action_type_id=2)
            # DO NOT WRAP CURL LINE
            proc = subprocess.Popen(
                "curl -Ss -F type=composer -F client_id=%s -F \"api_key=%s\" -F synchronous=1 -F id=%s -F post_action_type_id=2 \"%s/post_actions\"" % (
                    config.DISCOURSE_CLIENT_ID, config.DISCOURSE_API_KEY, post_id, config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER),
                stdout=subprocess.PIPE, shell=True)
            response_post_like = proc.stdout.read()
            logger.info(
                'Post %s voted by user ID %s! [ OK ]' % (post_id, voter))
        else:
            logger.error("Post not found!")
            continue

        # update Discourse vote with original voter
        query_vote_update_user_id = """
        update post_actions
        set user_id = %s,
            created_at = %s, updated_at = %s
        where post_id = %s
            and user_id = -1
            and post_action_type_id = %s"""
        vars_vote_update_user_id = (
            voter,
            post_vote_date, post_vote_date,
            post_id,
            2)
        cursor_pgsql.execute(query_vote_update_user_id, vars_vote_update_user_id)

        # update Discourse user actions (1)
        query_update_like_notification = """
            update user_actions
            set user_id = %s,
                acting_user_id = %s,
                created_at = %s, updated_at = %s
            where target_post_id = %s
                and user_id = -1
                and acting_user_id = -1
                and action_type = %s"""
        vars_update_like_notification = (
            voter,
            voter,
            post_vote_date, post_vote_date,
            post_id,
            1)
        cursor_pgsql.execute(query_update_like_notification, vars_update_like_notification)

        # update Discourse user actions (2)
        query_update_given_like = """
            update user_actions
            set acting_user_id = %s,
                created_at = %s, updated_at = %s
            where target_post_id = %s
                and acting_user_id = -1
                and action_type = %s"""
        vars_update_given_like = (
            voter,
            post_vote_date, post_vote_date,
            post_id,
            2)
        cursor_pgsql.execute(query_update_given_like, vars_update_given_like)

        # commit each cycle
        conn_pgsql.commit()

        endTs = time.time()
        interval = (endTs - startTs) * 1000

        logger.info('Post voted in %s ms.' % interval)

        x += 1

    post_votes = cursor_get_post_votes_info.fetchmany(250)

    i += 250

conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')
