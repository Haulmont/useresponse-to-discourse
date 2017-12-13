# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import json
import config
import humanize
import platform
import subprocess
import psycopg2
import logging
import MySQLdb.cursors
from logging.handlers import RotatingFileHandler
from pydiscourse import DiscourseClient

reload(sys)
sys.setdefaultencoding('utf8')

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = RotatingFileHandler('migrate_attachments.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate ATTACHMENTS.\n')

# ===================================================================
# connect to Discourse
# ===================================================================

logger.info('Connecting to Discourse...')
discourse = DiscourseClient(
    config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER + '/' + config.DISCOURSE_FOLDER,
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

cursor_get_topic_attachments_info = useresponse_db.cursor()
cursor_get_post_attachments_info = useresponse_db.cursor()
cursor_find_matched_topic = useresponse_db.cursor()
cursor_find_matched_post = useresponse_db.cursor()

# TOPICS

# select all attachments for topics
logger.info('Reading attachments for topics...')
topic_attachments = "select id, owner, object_id, name, location from ur_attachments where owner like 'object%';"
cursor_get_topic_attachments_info.execute(topic_attachments)

topic_attachments = cursor_get_topic_attachments_info.fetchall()

# iterate attachments
logger.info('Found %s attachments!' % len(topic_attachments))

x = 1

# iterate attachments by id
for attachment in topic_attachments:
    # time.sleep(0.05)

    startTs = time.time()

    # read attachments
    topic_attachment_id = attachment['id']
    topic_attachment_filename = attachment['name']
    topic_attachment_basename = os.path.splitext(attachment['name'])[0]
    topic_attachment_object_id = attachment['object_id']
    topic_attachment_type = attachment['owner']
    topic_attachment_location = attachment['location']
    topic_attachment_filename_extension = os.path.splitext(topic_attachment_filename)[1][1:]
    topic_attachment_location_extension = os.path.splitext(topic_attachment_location)[1][1:]

    # BEGIN of custom block #
    # You probably don't need this block, because in my case some attachments didn't have extensions
    # but since ID=1165 attachments began storing a file extension.
    #
    if topic_attachment_id < 1165:  # explanation: starting from 1165, we have locations with file extension
        # Compose filepath and filename
        # Check for illegal symbols in the filename
        if not re.match('^[\w ().-]+$', topic_attachment_basename):
            topic_attachment_fullname = topic_attachment_location + '.' + topic_attachment_filename_extension
        else:
            topic_attachment_fullname = topic_attachment_filename
    else:  # for locations with extensions, id >= 1165
        if not re.match('^[\w ().-]+$', topic_attachment_basename):
            topic_attachment_fullname = topic_attachment_location
        else:
            topic_attachment_fullname = topic_attachment_filename
    #
    # END of custom block #

    if platform.system() == 'Windows':
        old_path = os.path.join(os.getcwd() + '\\attachments', topic_attachment_location)
        new_path = os.path.join(os.getcwd() + '\\attachments', topic_attachment_fullname)
    else:
        old_path = os.path.join(os.getcwd() + '/attachments', topic_attachment_location)
        new_path = os.path.join(os.getcwd() + '/attachments', topic_attachment_fullname)

    try:
        # rename attachment
        os.rename(old_path, new_path)
    except Exception, ex:
        logger.error('Error during renaming.' + ex.message, exc_info=True)

    logger.info('%d/%s. Migrating attachment for topic: %s (location: %s), original topic: %s' % (
        x, len(topic_attachments), topic_attachment_filename, topic_attachment_location, topic_attachment_object_id))

    # find matched topic
    query_find_matched_topic = "select discourse_id from match_topics where useresponse_id = %s;"
    vars_find_matched_topic = topic_attachment_object_id
    cursor_find_matched_topic.execute(query_find_matched_topic, (vars_find_matched_topic,))
    topic = cursor_find_matched_topic.fetchone()

    try:
        discourse_topic_id = topic['discourse_id']
    except Exception, ex:
        logger.warning("Topic not found." + ex.message, exc_info=True)
        continue

    # upload file to discourse API endpoint, then use it
    # DO NOT WRAP CURL COMMAND LINE
    proc = subprocess.Popen(
        "curl -Ss -F type=composer -F client_id=%s -F \"files[]=@%s\" \"%s/uploads.json?api_key=%s&synchronous=1\"" % (
            config.DISCOURSE_CLIENT_ID, new_path, config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER, config.DISCOURSE_API_KEY),
        stdout=subprocess.PIPE, shell=True)
    response_upload = proc.stdout.read()

    # read post=1 in topic
    query_get_post_body = "select id, raw from posts where topic_id = %s and post_number = 1;"
    vars_get_post_body = (discourse_topic_id,)
    cursor_pgsql.execute(query_get_post_body, vars_get_post_body)

    # get original body content
    response_sql = cursor_pgsql.fetchone()
    post_id = response_sql[0]
    old_body = response_sql[1]

    try:
        # parse API-upload response
        response_upload_json = json.loads(response_upload)
        attachment_extension = response_upload_json['extension']
        attachment_filesize = response_upload_json['filesize']
        attachment_height = response_upload_json['height']
        attachment_width = response_upload_json['width']
        attachment_short_url = response_upload_json['short_url']
        attachment_url = response_upload_json['url']

        # iterate pictures
        if (attachment_extension == 'jpg') or (
                    attachment_extension == 'JPG') or (
                    attachment_extension == 'png') or (
                    attachment_extension == 'PNG') or (
                    attachment_extension == 'jpeg') or (
                    attachment_extension == 'JPEG'):
            new_body = old_body + '\n\n' + '![%s|%sx%s](%s)' % (
                topic_attachment_basename, attachment_width, attachment_height, attachment_short_url)
            discourse.update_post(post_id, new_body, '')
        else:
            # iterate generic attachments
            new_body = old_body + '\n\n' + '<a class="attachment" href="%s">%s</a> (%s)' % (
                attachment_url, topic_attachment_filename, humanize.naturalsize(attachment_filesize, gnu=True))
            discourse.update_post(post_id, new_body, '')

    except Exception, ex:
        logger.error("Error during parsing JSON: " + response_upload + ex.message, exc_info=True)
    finally:
        try:
            # remove processed file from local disk
            os.remove(new_path)
        except Exception, ex:
            logger.error('Cannot remove file!' + ex.message, exc_info=True)

    endTs = time.time()
    interval = (endTs - startTs) * 1000

    logger.info('Attachment uploaded in %s msec.' % interval)

    x += 1

# POSTS
# comments the same as for topics

logger.info('Reading attachments for posts...')
post_attachments = "select id, owner, object_id, name, location from ur_attachments where owner like 'comment%';"
cursor_get_post_attachments_info.execute(post_attachments)

post_attachments = cursor_get_post_attachments_info.fetchall()

# iterate attachments
logger.info('Found %s attachments!' % len(post_attachments))

x = 1

for attachment in post_attachments:
    # time.sleep(0.05)

    startTs = time.time()

    post_attachment_id = attachment['id']
    post_attachment_filename = attachment['name']
    post_attachment_basename = os.path.splitext(attachment['name'])[0]
    post_attachment_object_id = attachment['object_id']
    post_attachment_type = attachment['owner']
    post_attachment_location = attachment['location']
    post_attachment_filename_extension = os.path.splitext(post_attachment_filename)[1][1:]
    post_attachment_location_extension = os.path.splitext(post_attachment_location)[1][1:]

    if post_attachment_id < 1165: # see the explanation above in the topic's section
        if not re.match('^[\w ().-]+$', post_attachment_basename):
            post_attachment_fullname = post_attachment_location + '.' + post_attachment_filename_extension
        else:
            post_attachment_fullname = post_attachment_filename
    else:
        if not re.match('^[\w ().-]+$', post_attachment_basename):
            post_attachment_fullname = post_attachment_location
        else:
            post_attachment_fullname = post_attachment_filename

    if platform.system() == 'Windows':
        old_path = os.path.join(os.getcwd() + '\\attachments', post_attachment_location)
        new_path = os.path.join(os.getcwd() + '\\attachments', post_attachment_fullname)
    else:
        old_path = os.path.join(os.getcwd() + '/attachments', post_attachment_location)
        new_path = os.path.join(os.getcwd() + '/attachments', post_attachment_fullname)

    try:
        os.rename(old_path, new_path)
    except Exception, ex:
        logger.warning('Error during renaming.' + ex.message, exc_info=True)

    logger.info('%d/%s. Migrating attachment for post: %s (location: %s), original post: %s' % (
        x, len(post_attachments), post_attachment_filename, post_attachment_location, post_attachment_object_id))

    # find matched post
    query_find_matched_post = "select discourse_comment_id from match_comments where useresponse_comment_id = %s;"
    vars_find_matched_post = post_attachment_object_id
    cursor_find_matched_post.execute(query_find_matched_post, (vars_find_matched_post,))
    post = cursor_find_matched_post.fetchone()

    try:
        discourse_post_id = post['discourse_comment_id']
    except Exception, ex:
        logger.warning("Post not found." + ex.message, exc_info=True)
        continue

    # DO NOT WRAP CURL COMMAND LINE
    proc = subprocess.Popen(
        "curl -Ss -F type=composer -F client_id=%s -F \"files[]=@%s\" \"%s/uploads.json?api_key=%s&synchronous=1\"" % (
            config.DISCOURSE_CLIENT_ID, new_path, config.DISCOURSE_BASE_URL + '/' + config.DISCOURSE_FOLDER + '/' + config.DISCOURSE_FOLDER, config.DISCOURSE_API_KEY),
        stdout=subprocess.PIPE, shell=True)
    response_upload = proc.stdout.read()

    # read post
    query_get_post_body = "select id, raw from posts where id = %s;"
    vars_get_post_body = (discourse_post_id,)
    cursor_pgsql.execute(query_get_post_body, vars_get_post_body)

    response_sql = cursor_pgsql.fetchone()
    post_id = response_sql[0]
    old_body = response_sql[1]

    try:
        response_upload_json = json.loads(response_upload)
        attachment_extension = response_upload_json['extension']
        attachment_filesize = response_upload_json['filesize']
        attachment_height = response_upload_json['height']
        attachment_width = response_upload_json['width']
        attachment_short_url = response_upload_json['short_url']
        attachment_url = response_upload_json['url']

        # iterate pictures
        if (attachment_extension == 'jpg') or (
                    attachment_extension == 'JPG') or (
                    attachment_extension == 'png') or (
                    attachment_extension == 'PNG') or (
                    attachment_extension == 'jpeg') or (
                    attachment_extension == 'JPEG'):
            new_body = old_body + '\n\n' + '![%s|%sx%s](%s)' % (
                post_attachment_basename, attachment_width, attachment_height, attachment_short_url)
            # update post with the picture
            discourse.update_post(post_id, new_body, '')
        # iterate generic attachments
        else:
            new_body = old_body + '\n\n' + '<a class="attachment" href="%s">%s</a> (%s)' % (
                attachment_url, post_attachment_filename, humanize.naturalsize(attachment_filesize, gnu=True))
            # update post with the attachment
            discourse.update_post(post_id, new_body, '')

    except Exception, ex:
        logger.error("Error during parsing JSON: " + response_upload + ex.message, exc_info=True)
    finally:
        try:
            os.remove(new_path)
        except Exception, ex:
            logger.error('Cannot remove file!' + ex.message, exc_info=True)

    endTs = time.time()
    interval = (endTs - startTs) * 1000

    logger.info('Attachment uploaded in %s ms.' % interval)

    x += 1

conn_pgsql.close()
useresponse_db.close()

logger.info('Done.')
