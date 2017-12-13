# -*- coding: utf-8 -*-

import sys
import config
import logging
import MySQLdb.cursors
import psycopg2.extensions
from logging.handlers import RotatingFileHandler
from pydiscourse import DiscourseClient

reload(sys)
sys.setdefaultencoding('utf8')

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = RotatingFileHandler('migrate_owners.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('CHANGE OWNER.\n')

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

cursor_match_topics = useresponse_db.cursor()
cursor_topic_starter_ur = useresponse_db.cursor()
cursor_topic_starter_ds = useresponse_db.cursor()
cursor_frequent_posters_ur = useresponse_db.cursor()

cursor_get_last_reply = useresponse_db.cursor()
cursor_reply_to = useresponse_db.cursor()

cursor_match_comments = useresponse_db.cursor()
cursor_commenter_ur = useresponse_db.cursor()
cursor_commenter_ds = useresponse_db.cursor()

# query for topics
query_match_topics = "select id, useresponse_id, discourse_id, views from match_topics;"
cursor_match_topics.execute(query_match_topics)

i = 0

topics = cursor_match_topics.fetchmany(250)

# TOPICS
logger.info('Reading topics...')
while topics:

    x = 1

    # iterate topics by id
    for topic in topics:
        logger.info('%d/%d. Topic ID: %s' % (i, x, topic['id']))
        # read original topic starter id
        cursor_topic_starter_ur.execute(
            "select created_by_id from ur_objects where id = %s;", (topic['useresponse_id'],))
        result_topic_starter_ur = cursor_topic_starter_ur.fetchone()
        topic_starter_ur = result_topic_starter_ur['created_by_id']

        # match user by match_users table
        cursor_topic_starter_ds.execute(
            "select discourse_id from match_users where useresponse_id = %s;", (topic_starter_ur,))
        result_topic_starter_ds = cursor_topic_starter_ds.fetchone()
        if result_topic_starter_ds != None:
            topic_starter_ds = result_topic_starter_ds['discourse_id']
            logger.info('Topic starter: %s\n' % topic_starter_ds)
        else:
            topic_starter_ds = -2
            logger.warning('Topic starter: BOT\n')

        # update Discourse topic with original author - field 'Created'
        query_topic = "update topics set views = %s, user_id = %s where id = %s"
        vars_topic = (int(topic['views']), int(topic_starter_ds), int(topic['discourse_id']))
        cursor_pgsql.execute(query_topic, vars_topic)

        # update Discourse topic with original author (top left icon and caption)
        query_main_post = "update posts set user_id = %s where topic_id = %s and post_number = 1"
        vars_main_post = (int(topic_starter_ds), int(topic['discourse_id'])
                          )
        cursor_pgsql.execute(query_main_post, vars_main_post)

        # update post_timings
        query_post_timings = """
        update post_timings set user_id = %s where topic_id = %s and post_number = 1 and user_id = -1"""
        vars_post_timings = (int(topic_starter_ds), int(topic['discourse_id']))
        cursor_pgsql.execute(query_post_timings, vars_post_timings)

        # update most recent topic users
        query_most_recent_topic = "update topic_users set user_id = %s where topic_id = %s and user_id = -1"
        vars_most_recent_topic = (int(topic_starter_ds), int(topic['discourse_id']))
        cursor_pgsql.execute(query_most_recent_topic, vars_most_recent_topic)

        # update last_reply
        query_get_last_reply = """select b.discourse_id from ur_comments a, match_users b
        where a.object_id = %s and a.created_by_id = b.useresponse_id order by a.created_at desc limit 1;"""
        vars_get_last_reply = int(topic['useresponse_id'])
        cursor_get_last_reply.execute(query_get_last_reply, (vars_get_last_reply,))
        last_reply = cursor_get_last_reply.fetchone()

        if last_reply != None:
            last_reply_id = last_reply['discourse_id']
        else:
            last_reply_id = -2
            logger.warning('Last replied user = BOT!')

        query_update_last_reply = "update topics set last_post_user_id = %s where id = %s"
        vars_update_last_reply = (last_reply_id, topic['discourse_id'])
        cursor_pgsql.execute(query_update_last_reply, vars_update_last_reply)

        # update frequent posters
        #
        # If you get an exception like:
        # _mysql_exceptions.OperationalError: (1055...)
        # then you need to run following SQLs first:
        #
        # mysql> set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
        # mysql> set session sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
        #
        query_frequent_posters = """
        select count(b.discourse_id),
            a.created_by_id,
            a.created_at,
            a.updated_at,
            b.discourse_id
        from ur_comments a, match_users b
        where a.object_id = %s
            and a.created_by_id = b.useresponse_id
        group by b.discourse_id
        order by count(b.discourse_id)
        desc limit 4;
        """
        vars_frequent_posters = (topic['useresponse_id'],)
        cursor_frequent_posters_ur.execute(query_frequent_posters, vars_frequent_posters)
        frequent_users = cursor_frequent_posters_ur.fetchall()

        if len(frequent_users) > 0:
            query_frequent_poster_4 = "update topics set featured_user1_id = %s where id = %s"
            vars_frequent_poster_4 = ((frequent_users[0]['discourse_id']), topic['discourse_id'])
            cursor_pgsql.execute(query_frequent_poster_4, vars_frequent_poster_4)

        if len(frequent_users) > 1:
            query_frequent_poster_3 = "update topics set featured_user2_id = %s where id = %s"
            vars_frequent_poster_3 = ((frequent_users[1]['discourse_id']), topic['discourse_id'])
            cursor_pgsql.execute(query_frequent_poster_3, vars_frequent_poster_3)

        if len(frequent_users) > 2:
            query_frequent_poster_2 = "update topics set featured_user3_id = %s where id = %s"
            vars_frequent_poster_2 = ((frequent_users[2]['discourse_id']), topic['discourse_id'])
            cursor_pgsql.execute(query_frequent_poster_2, vars_frequent_poster_2)

        if len(frequent_users) > 3:
            query_frequent_poster_1 = "update topics set featured_user4_id = %s where id = %s"
            vars_frequent_poster_1 = ((frequent_users[3]['discourse_id']), topic['discourse_id'])
            cursor_pgsql.execute(query_frequent_poster_1, vars_frequent_poster_1)

        x += 1

    conn_pgsql.commit()
    topics = cursor_match_topics.fetchmany(250)

    i += 250

# FIX: update last_post_user_id for topics without answers
query_update_single_topics = "update topics set last_post_user_id = user_id where posts_count = 1"  # user_id != -2
cursor_pgsql.execute(query_update_single_topics)

# COMMENTS

match_comments = """
select useresponse_topic_id,
    useresponse_comment_id,
    discourse_topic_id,
    discourse_comment_id,
    discourse_post_number
from match_comments;
"""
cursor_match_comments.execute(match_comments)

i = 0

comments = cursor_match_comments.fetchmany(250)

logger.info('Reading comments...')
while comments:

    x = 1

    # iterate topics by id
    for comment in comments:
        # read comments matching table
        useresponse_topic_id = comment['useresponse_topic_id']
        useresponse_comment_id = comment['useresponse_comment_id']
        discourse_topic_id = comment['discourse_topic_id']
        discourse_comment_id = comment['discourse_comment_id']
        discourse_post_number = comment['discourse_post_number']

        logger.info('%d/%d. Comment/topic IDs: %s/%s --> %s/%s' % (
            i, x, useresponse_comment_id, useresponse_topic_id, discourse_comment_id,
            discourse_topic_id))

        # read original commenter id
        cursor_commenter_ur.execute("select created_by_id from ur_comments where id = %s;", (useresponse_comment_id,))
        result_commenter_ur = cursor_commenter_ur.fetchone()
        commenter_ur = result_commenter_ur['created_by_id']

        # match user by match_users table
        cursor_commenter_ds.execute(
            "select discourse_id from match_users where useresponse_id = %s;", (commenter_ur,))
        result_commenter_ds = cursor_commenter_ds.fetchone()

        if result_commenter_ds != None:
            commenter_ds = result_commenter_ds['discourse_id']
            logger.info('Commenter ID: %s\n' % commenter_ds)
        else:
            # default commenter: bot
            commenter_ds = -2
            logger.warning('Commenter: BOT\n')

        # update Discourse comment with original author (top left icon and caption)
        query_post = "update posts set user_id = %s where topic_id = %s and id = %s and post_number != 1"
        vars_post = (int(commenter_ds), int(comment['discourse_topic_id']), int(comment['discourse_comment_id']))
        cursor_pgsql.execute(query_post, vars_post)

        # update most recent posters
        query_most_recent_post = """
                    update post_timings set user_id = %s where topic_id = %s and post_number = %s and user_id = -1"""
        vars_most_recent_post = (int(commenter_ds), int(discourse_topic_id), int(discourse_post_number))
        cursor_pgsql.execute(query_most_recent_post, vars_most_recent_post)

        x += 1

    conn_pgsql.commit()
    comments = cursor_match_comments.fetchmany(250)

    i += 250

cursor_pgsql.close()
conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')

logger.info('#####################################')
logger.info('# If unicorn was stopped, start it: #')
logger.info('# /var/discourse/launcher enter app #')
logger.info('# sv start unicorn                  #')
logger.info('#####################################\n')
