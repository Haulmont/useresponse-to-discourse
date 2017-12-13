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

logfile_handler = RotatingFileHandler('migrate_topic_votes.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate TOPIC VOTES.\n')

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
cursor_find_matched_voter = useresponse_db.cursor()
cursor_find_comment_author = useresponse_db.cursor()

# TOPICS

# select all votes for topics
logger.info('Reading votes for topics...')
query_get_topic_votes = """
select v.object_id as 'vote_id',
       v.created_by_id as 'vote_user_id',
       t.id as 'topic_id',
       t.created_by_id as 'topic_user_id',
       v.created_at
from ur_votes v join
     ur_objects t
     on v.object_id = t.id
where v.created_by_id <> t.created_by_id
      and v.value <> 0
      and v.owner like 'object'
      order by v.created_at
"""
cursor_get_topic_votes_info.execute(query_get_topic_votes)

i = 0

topic_votes = cursor_get_topic_votes_info.fetchmany(250)

while topic_votes:

    x = 1

    # iterate votes by id
    for vote in topic_votes:
        # time.sleep(0.05)

        startTs = time.time()

        # read votes
        topic_vote_object_id = vote['topic_id']
        topic_vote_by_user = vote['vote_user_id']
        topic_vote_date = vote['created_at']

        logger.info('%d/%d. Migrating like for topic ID: %s voted by user ID: %s on %s' % (
            i, x, topic_vote_object_id, topic_vote_by_user, topic_vote_date))

        # find matched topic
        query_find_matched_topic = "select discourse_id from match_topics where useresponse_id = %s;"
        vars_find_matched_topic = topic_vote_object_id
        cursor_find_matched_topic.execute(query_find_matched_topic, (vars_find_matched_topic,))
        topic = cursor_find_matched_topic.fetchone()

        if topic:
            discourse_topic_id = topic['discourse_id']
            # read post=1 in topic
            query_get_post_body = "select id from posts where topic_id = %s and post_number = 1;"
            vars_get_post_body = (discourse_topic_id,)
            cursor_pgsql.execute(query_get_post_body, vars_get_post_body)
            response_sql = cursor_pgsql.fetchone()
            discourse_post_id = response_sql[0]

            # find matched topicstarter
            query_find_topicstarter = "select user_id from topics where id = %s;"
            vars_find_topicstarter = (discourse_topic_id,)
            cursor_pgsql.execute(query_find_topicstarter, vars_find_topicstarter)
            topic_starter = cursor_pgsql.fetchone()

            # find matched topic voter
            query_find_matched_voter = "select discourse_id from match_users where useresponse_id = %s;"
            vars_find_matched_voter = topic_vote_by_user
            cursor_find_matched_voter.execute(query_find_matched_voter, (vars_find_matched_voter,))
            user = cursor_find_matched_voter.fetchone()

            try:
                voter = user['discourse_id']
            except Exception, ex:
                logger.error("User not found!" + ex.message, exc_info=True)
                voter = -2

            # post a like using API (action_type = 2)
            # DO NOT WRAP CURL COMMAND
            proc = subprocess.Popen(
                "curl -Ss -F type=composer -F client_id=%s -F \"api_key=%s\" -F synchronous=1 -F id=%s -F post_action_type_id=2 \"%s/post_actions\"" % (
                    config.DISCOURSE_CLIENT_ID, config.DISCOURSE_API_KEY, discourse_post_id, config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER),
                stdout=subprocess.PIPE, shell=True)
            response_post_like = proc.stdout.read()
            logger.info(
                'Topic %s (post %s) voted by %s! [ OK ]' % (discourse_topic_id, discourse_post_id, voter))
        else:
            logger.warning("Topic not found!")
            continue

        # update Discourse vote with original voter (post_actions)
        query_update_vote_user_id = """
            update post_actions
            set user_id = %s,
                created_at = %s, updated_at = %s
            where user_id = -1 
                and post_action_type_id = %s"""
        vars_update_vote_user_id = (
            voter,
            topic_vote_date, topic_vote_date,
            2)
        cursor_pgsql.execute(query_update_vote_user_id, vars_update_vote_user_id)

        # update Discourse user actions (1) - update notification to user was been liked
        query_update_like_notification = """
            update user_actions
            set user_id = %s,
                acting_user_id = %s,
                created_at = %s, updated_at = %s
            where target_topic_id = %s
                and target_post_id = %s
                and user_id = -1
                and acting_user_id = -1
                and action_type = %s"""
        vars_update_like_notification = (
            voter,
            voter,
            topic_vote_date, topic_vote_date,
            discourse_topic_id,
            discourse_post_id,
            1)
        cursor_pgsql.execute(query_update_like_notification, vars_update_like_notification)

        # update Discourse user actions (2) - update given likes in user's activity profile
        query_update_given_like = """
            update user_actions
            set acting_user_id = %s,
                created_at = %s, updated_at = %s
            where target_topic_id = %s
                and target_post_id = %s
                and acting_user_id = -1
                and action_type = %s"""
        vars_update_given_like = (
            voter,
            topic_vote_date, topic_vote_date,
            discourse_topic_id,
            discourse_post_id,
            2)
        cursor_pgsql.execute(query_update_given_like, vars_update_given_like)

        # commit each line in the cycle
        conn_pgsql.commit()

        endTs = time.time()
        interval = (endTs - startTs) * 1000

        logger.info('Topic voted in %s msec.' % interval)

        x += 1

    topic_votes = cursor_get_topic_votes_info.fetchmany(250)

    i += 250

conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')
