# -*- coding: utf-8 -*-

import sys
import time
import config
import logging
import psycopg2
import MySQLdb.cursors
from logging.handlers import RotatingFileHandler
from pydiscourse import DiscourseClient

reload(sys)
sys.setdefaultencoding('utf8')

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = RotatingFileHandler('migrate_comments.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate COMMENTS.\n')

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
    useresponse_db = MySQLdb.connect(use_unicode=True, charset='utf8', host=(config.USERESPONSE_DATABASE_HOST),
                                     port=(config.USERESPONSE_DATABASE_PORT),
                                     user=(config.USERESPONSE_DATABASE_LOGIN),
                                     passwd=(config.USERESPONSE_DATABASE_PASSWORD),
                                     db=(config.USERESPONSE_DATABASE_NAME),
                                     cursorclass=MySQLdb.cursors.DictCursor)
except MySQLdb.Error, e:
    logger.error('Error %d: %s' % (e.args[0], e.args[1]))
    sys.exit(1)

cursor_useresponse = useresponse_db.cursor()

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
# query create matching table
# ===================================================================

logger.info('Creating table matching table if not exists...')
match_comments = """
create table if not exists match_comments
(
    id INT primary key auto_increment,
    useresponse_topic_id INT,
    useresponse_comment_id INT,
    useresponse_comment_reply_to_id INT,
    useresponse_author_id INT,
    discourse_topic_id INT,
    discourse_comment_id INT,
    discourse_post_number INT,
    discourse_post_author_id INT
)
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8
    DEFAULT COLLATE utf8_unicode_ci
    """
cursor_useresponse.execute(match_comments)

# ===================================================================
# queries select from table
# ===================================================================

cursor_useresponse_topics = useresponse_db.cursor()
cursor_useresponse_users = useresponse_db.cursor()
cursor_match_user = useresponse_db.cursor()
cursor_useresponse_comments = useresponse_db.cursor()
cursor_get_topic_issues = useresponse_db.cursor()
cursor_find_parent_topic = useresponse_db.cursor()

# select all comments
logger.info('Reading topics...')
match_topics = "select id, useresponse_id, discourse_id from match_topics;"
cursor_useresponse_topics.execute(match_topics)

i = 0

topics = cursor_useresponse_topics.fetchmany(250)

while topics:

    # iterate topics by id
    for topic in topics:
        # time.sleep(0.05)

        # read matched topic id
        useresponse_id = topic['useresponse_id']
        discourse_id = topic['discourse_id']

        # read useresponse comments
        comments = """
        select id,
            content,
            object_id,
            reply_to,
            created_by_id,
            created_at
        from ur_comments
        where deleted_at is null
            and object_id = %s;
            """
        cursor_useresponse_comments.execute(comments, (useresponse_id,))
        all_comments = cursor_useresponse_comments.fetchall()

        x = 1

        for comment in all_comments:
            # time.sleep(0.05)

            if comment['reply_to'] != 0:
                reply_to = comment['reply_to']
            else:
                reply_to = None

            # check for empty body
            if len(comment['content']) > 2:
                # check for too long body (> 30000)
                if len(comment['content']) > 30000:
                    content_bbcode = comment['content'][
                                     :30000] + '\n[/code]\n' + "\n:evergreen_tree: _The text has been truncated to the first 30000 characters._"
                    logger.warning('Body length was >32000, original topic/comment ID: %s/%s' % (
                        comment['object_id'], comment['id']))
            else:
                content_bbcode = 'Subj, or see the attachment, please.'
                logger.warning('Comment is empty or has only an attachment!')

            # replace [pre], [/pre] to bbcode
            content_bbcode = comment['content'] \
                .replace("[pre]", "\n[code]\n") \
                .replace("[/pre]", "\n[/code]\n") \
                .replace("[ol]", "<ol>") \
                .replace("[/ol]", "</ol>") \
                .replace("[ul]", "<ul>") \
                .replace("[/ul]", "</ul>") \
                .replace("[li]", "<li>") \
                .replace("[/li]", "</li>") \
                .replace("[list]", "<list>") \
                .replace("[/list]", "</list>") \
                .replace("[b]", "<b>") \
                .replace("[/b]", "</b>") \
                .replace("[i]", "<i>") \
                .replace("[/i]", "</i>") \
                .replace("[s]", "<s>") \
                .replace("[/s]", "</s>") \
                .replace("[u]", "<u>") \
                .replace("[/u]", "</u>") \
                .replace("[img]", "<img>") \
                .replace("[/img]", "</img>")

            # fix internal links
            content_bbcode = content_bbcode.replace("https://www.example.com/support/topic",
                                                    "https://www.example.com/discuss/t")

            # warn if comment has a link to other comment
            if '#comment' in content_bbcode:
                logger.warning('Comment has an internal link to other comment. Fix it manually!')

            logger.info(
                '%d/%d/%s. Comment id: %s\n Topic id: %s\n Reply to comment id: %s\n Create by user id: %s\n Created at: %s\n' % (
                    i, x, len(all_comments), comment['id'], comment['object_id'], reply_to, comment['created_by_id'],
                    comment['created_at']))

            # match topic owner
            query_match_user = "select discourse_id from match_users where useresponse_id = %s;"
            vars_match_user = comment['created_by_id']
            cursor_match_user.execute(query_match_user, (vars_match_user,))
            user = cursor_match_user.fetchone()

            if user != None:
                user_id = user['discourse_id']
            else:
                logger.error('User ID=%s not found! Comment created by BOT!')
                user_id = -2

            try:
                logger.info('Migrating comment...')

                startTs = time.time()
                discourse_post = discourse.create_post(
                    content=content_bbcode, topic_id=discourse_id, created_at=comment['created_at'])

                query_user_actions = """
                update user_actions
                set user_id=%s,
                    acting_user_id=%s,
                    created_at=%s,
                    updated_at=%s
                where target_post_id=%s
                """
                vars_user_actions = (
                    user_id, user_id, comment['created_at'], comment['created_at'], discourse_post['id'])

                cursor_pgsql.execute(query_user_actions, vars_user_actions)

                endTs = time.time()
                interval = (endTs - startTs) * 1000

                logger.info("Migrated in %s ms" % interval)

                discourse_post_number = discourse_post['post_number']
                discourse_post_author_id = discourse_post['user_id']

                # insert line into matching table
                match_comment_query = """
                insert into match_comments
                (
                    useresponse_topic_id,
                    useresponse_comment_id,
                    useresponse_comment_reply_to_id,
                    useresponse_author_id,
                    discourse_topic_id,
                    discourse_comment_id,
                    discourse_post_number,
                    discourse_post_author_id
                )
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                match_comment_vars = (
                    int(topic['useresponse_id']),
                    int(comment['id']),
                    reply_to,
                    int(comment['created_by_id']),
                    int(topic['discourse_id']),
                    int(discourse_post['id']),
                    discourse_post_number,
                    discourse_post_author_id
                )
                cursor_useresponse.execute(match_comment_query, match_comment_vars)

            except Exception, ex:
                if 'Too Many Requests' in ex.message:
                    logger.error('Too Many Requests!')
                    exit(-15)

                logger.error("Error during migration: " + ex.message, exc_info=True)

            x += 1

        conn_pgsql.commit()
        useresponse_db.commit()

    topics = cursor_useresponse_topics.fetchmany(250)

    i += 250

conn_pgsql.commit()
conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')

logger.info('#####################################')
logger.info('# Recommended to stop Unicorn:      #')
logger.info('# /var/discourse/launcher enter app #')
logger.info('# sv stop unicorn then run          #')
logger.info('# discourse_change_owner.py script! #')
logger.info('#####################################\n')
