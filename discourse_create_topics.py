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

logfile_handler = RotatingFileHandler('migrate_topics.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate TOPICS.\n')

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

cursor_useresponse = useresponse_db.cursor()

# ===================================================================
# connect to postgres
# ===================================================================

logger.info('Connecting to Discourse (pgsql)...')
# Define our connection string
conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (
    config.DISCOURSE_DATABASE_HOST, config.DISCOURSE_DATABASE_PORT, config.DISCOURSE_DATABASE_NAME,
    config.DISCOURSE_DATABASE_LOGIN, config.DISCOURSE_DATABASE_PASSWORD)

# get a connection, if a connect cannot be made an exception will be raised here
conn_pgsql = psycopg2.connect(conn_string)

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cursor_pgsql = conn_pgsql.cursor()

# ===================================================================
# query create matching table
# ===================================================================

logger.info('Creating table matching table if not exists...')
match_topics = """
create table if not exists match_topics
(
    id INT not null auto_increment,
    primary key(id),
    useresponse_id INT,
    discourse_id INT,
    useresponse_slug VARCHAR(255),
    match_slug INT,
    discourse_slug VARCHAR(255),
    views INT
)
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8
    DEFAULT COLLATE utf8_unicode_ci
"""
cursor_useresponse.execute(match_topics)

# ===================================================================
# queries
# ===================================================================

cursor_get_topics = useresponse_db.cursor()
cursor_match_user = useresponse_db.cursor()

# select all topics except announcements
logger.info('Reading topics...')
query_get_topics = """
select  id,
        title,
        slug,
        content,
        object_type,
        category_id,
        created_by_id,
        created_at,
        commented_by_id,
        views
from ur_objects
where is_private != 1
        and module != 'announcements'
        and deleted_by_id = 0
        order by created_at asc;
        """
cursor_get_topics.execute(query_get_topics)

i = 0

topics = cursor_get_topics.fetchmany(250)

while topics:
    category = 'General Discussion'

    x = 1

    # iterate topics
    for topic in topics:  # While loops always make me shudder!
        # time.sleep(0.05)
        content_bbcode = topic['content']

        # check for duplicate (excluded) topics
        if topic['title'] not in config.EXCLUDE_TOPIC_LIST:
            topic_title = topic['title']
        else:
            topic_title = topic['title'] + ' #' + str(topic['id'])
            logger.warning('Topic title found in exclude list! Renamed: %s' % topic_title)

        # check for empty body
        if len(topic['content']) > 2:
            # check for too long body (> 30000)
            if len(topic['content']) > 30000:
                content_bbcode = topic['content'][
                                 :30000] + '\n[/code]\n' + "\n:evergreen_tree: _The text has been truncated to the first 30000 characters._"
                logger.warning('Body length was >32000, title: %s' % topic_title)
        else:
            content_bbcode = topic_title
            logger.warning('Topic is empty or has only an attachment!')

        # replace [pre], [/pre] to bbcode
        content_bbcode = content_bbcode \
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

        logger.info(
            '%d/%d. Migrating topic ID: %s\n Title: %s\n Type: %s\n Created at: %s\n Views: %s\n User: %s' % (
                i, x, topic['id'], topic_title, topic['object_type'], topic['created_at'],
                topic['views'], topic['created_by_id']))

        # iterate topics by predefined categories
        if ('question' in topic['object_type']) or ('problem' in topic['object_type']):
            category = 'Support'
        if 'idea' in topic['object_type']:
            category = 'Ideas'
        if 'thanks' in topic['object_type']:
            category = 'General Discussion'

        # match topic owner
        query_match_user = "select discourse_id from match_users where useresponse_id = %s;"
        vars_match_user = topic['created_by_id']
        cursor_match_user.execute(query_match_user, (vars_match_user,))
        user = cursor_match_user.fetchone()
        if user != None:
            user_id = user['discourse_id']
        else:
            logger.warning('User ID=%s not found! Topic created by BOT!' % topic['created_by_id'])
            user_id = -2

        try:
            logger.info('Call discourse')

            startTs = time.time()
            try:
                discourse_topic = discourse.create_post(content_bbcode, title=topic_title, category=category,
                                                        created_at=topic['created_at'])

                topic_id = discourse_topic['topic_id']
                slug_new = discourse_topic['topic_slug']
                slug_old = topic['slug']
                match_slug = 1

                if slug_new != slug_old:
                    match_slug = 0
                    logger.warning('Slugs are different! %s vs %s' % (slug_new, slug_old))

            except Exception, e:
                if 'Title has already been used' in e.message:
                    logger.error("Error during migration!" + ' ' + topic_title + ' ' + e.message, exc_info=True)
                    continue

                time.sleep(1)

                logger.warning('[!] RETRY after error, topic: ' + str(topic['id']) + ' . Update slug manually!')

                discourse_topic = discourse.create_post(
                    content_bbcode, title=topic_title, category=category, created_at=topic['created_at'])

                topic_id = discourse_topic['topic_id']
                slug_new = discourse_topic['topic_slug']
                slug_old = topic['slug']
                match_slug = 1

                if slug_new != slug_old:
                    match_slug = 0

            query_user_actions = """
            update user_actions
            set user_id=%s,
                acting_user_id=%s,
                created_at=%s,
                updated_at=%s
            where target_topic_id=%s
            """
            vars_user_actions = (
                user_id, user_id, topic['created_at'], topic['created_at'], discourse_topic['topic_id'])

            cursor_pgsql.execute(query_user_actions, vars_user_actions)

            endTs = time.time()
            interval = (endTs - startTs) * 1000

            logger.info("Migrated in %s ms" % interval)

            # insert line into matching table
            match_topic_query = """insert into match_topics
                                (useresponse_id, discourse_id, useresponse_slug, match_slug, discourse_slug, views)
                                values (%s, %s, %s, %s, %s, %s)"""
            match_topic_vars = (
                int(topic['id']), int(discourse_topic['topic_id']), slug_old, match_slug, slug_new, int(topic['views']))
            cursor_useresponse.execute(match_topic_query, match_topic_vars)

        except Exception, ex:
            if 'Title has already been used' in ex.message:
                logger.warning('Title: %s' % (topic_title) + ex.message)
                continue

            if 'Too Many Requests' in ex.message:
                logger.error('Too Many Requests!')
                exit(-15)

            logger.error("Error during migration!" + ' ' + topic_title + ' ' + ex.message, exc_info=True)
        finally:
            logger.info("\n")

        x += 1

    conn_pgsql.commit()
    useresponse_db.commit()

    topics = cursor_get_topics.fetchmany(250)

    i += 250

conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')
