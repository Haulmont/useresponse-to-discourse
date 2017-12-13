# -*- coding: utf-8 -*-

import sys
import config
import logging
import psycopg2
from logging.handlers import RotatingFileHandler
from pydiscourse import DiscourseClient

reload(sys)
sys.setdefaultencoding('utf8')

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = RotatingFileHandler('update_user_stats.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Update USER STATS.\n')

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
# connect to postgres
# ===================================================================

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
# queries select users from table
# ===================================================================

# select all users incl. deleted
logger.info('Reading Discourse users...')
query_all_users = "select id, name from users where id > 1"
cursor_pgsql.execute(query_all_users)
users = cursor_pgsql.fetchall()

# iterate users
logger.info('Found %s users!' % len(users))

# reset stats for system
logger.info('Reset statistics for system users...')
query_reset_system_users = """
update user_stats 
set topics_entered = 0, 
    posts_read_count = 0, 
    time_read = 0, 
    days_visited = 0, 
    first_post_created_at = null
where (user_id = -1 or user_id = 1)
"""
cursor_pgsql.execute(query_reset_system_users)

conn_pgsql.commit()

for user in users:
    # time.sleep(0.05)

    # get account info
    user_id = user[0]
    user_name = user[1]

    # reset stats for user
    logger.info('Reset statistics for user %s (%s)...' % (user_name, user_id))
    query_reset_user_stats = """
    update user_stats 
    set topics_entered = 0, 
        posts_read_count = 0, 
        time_read = 0, 
        days_visited = 0, 
        first_post_created_at = null 
    where user_id = %s
    """
    vars_reset_user_stats = (user_id,)
    cursor_pgsql.execute(query_reset_system_users, vars_reset_user_stats)

    # select count likes given
    query_get_likes_given = """
    select count(*) as Likes_given 
    from user_actions 
    where action_type = 1 
        and user_id = %s"""
    vars_get_likes_given = (user_id,)
    cursor_pgsql.execute(query_get_likes_given, vars_get_likes_given)
    likes = cursor_pgsql.fetchone()

    # update likes given in user statistics
    query_update_likes_given = "update user_stats set likes_given = %s where user_id = %s"
    vars_update_likes_given = (likes[0], (user_id,))
    cursor_pgsql.execute(query_update_likes_given, vars_update_likes_given)

    conn_pgsql.commit()

cursor_pgsql.close()
conn_pgsql.close()

logger.info('Done.')
