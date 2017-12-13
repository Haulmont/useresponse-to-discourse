# -*- coding: utf-8 -*-

import sys
import re
import config
import random
import string
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

logfile_handler = RotatingFileHandler('migrate_users.log', backupCount=3)
logfile_handler.setFormatter(logging.Formatter(('%(asctime)s %(levelname)s %(message)s')))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

logger.info('\nMigrate UseResponse to Discourse.')
logger.info('Migrate USERS.\n')

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
# connect to services
# ===================================================================

# connect to useresponse database
logger.info('Connecting to UseResponse (mysql) %s:%s...' % (config.DRUPAL_DATABASE_HOST, config.DRUPAL_DATABASE_PORT))
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

# connect to drupal database
logger.info('Connecting to Drupal (mysql) %s:%s...' % (config.DRUPAL_DATABASE_HOST, config.DRUPAL_DATABASE_PORT))
try:
    drupal_db = MySQLdb.connect(use_unicode=True, charset='utf8',
                                host=(config.DRUPAL_DATABASE_HOST),
                                port=(config.DRUPAL_DATABASE_PORT),
                                user=(config.DRUPAL_DATABASE_LOGIN),
                                passwd=(config.DRUPAL_DATABASE_PASSWORD),
                                db=(config.DRUPAL_DATABASE_NAME),
                                cursorclass=MySQLdb.cursors.DictCursor)
except MySQLdb.Error, e:
    logger.error('Error %d: %s' % (e.args[0], e.args[1]))
    sys.exit(1)

cursor_drupal = drupal_db.cursor()

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
# query create matching table
# ===================================================================

logger.info('Creating matching table if not exists...')
match_users = """
create table if not exists match_users
(
    id INT not null auto_increment,
    primary key(id),
    useresponse_id INT,
    email VARCHAR(64),
    drupal_login VARCHAR(64),
    discourse_id INT,
    registration_ip VARCHAR(64)
)
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8
    DEFAULT COLLATE utf8_unicode_ci
    """
cursor_useresponse.execute(match_users)

# ===================================================================
# queries select from table
# ===================================================================

# select all users incl. deleted
logger.info('Reading UseResponse users...')
useresponse_users = "select id, full_name, email, created_at, updated_at, logged_at, last_activity, state from ur_users where state = 1"
cursor_useresponse.execute(useresponse_users)
all_useresponse_users = cursor_useresponse.fetchall()

# iterate users
logger.info('Found %s users!' % len(all_useresponse_users))

x = 1

for user in all_useresponse_users:
    email = str(user['email'])
    logger.info('')
    logger.info('Email: %s' % email)
    # time.sleep(0.05)

    # get account info
    user_created_at = user['created_at']
    user_updated_at = user['updated_at']
    user_last_seen_at = user['logged_at']
    user_last_posted_at = user['last_activity']

    # get registration IP address
    registration_ip = "select ip from ur_users_data where user_id = %s;"
    cursor_useresponse.execute(registration_ip, (user['id'],))
    registration_ip_result = cursor_useresponse.fetchall()

    if len(registration_ip_result) == 0:
        registration_ip_result = [{'ip': None}]

    reg_ip = registration_ip_result[0]['ip']
    logger.info('Registration: %s' % reg_ip)

    if email in config.STOP_MAIL_LIST:
        logger.warning('Email found in stop list! Email: %s' % email)
        continue

    # get DRUPAL_login by USERESPONSE_id
    drupal_login = "select uid, name from `users` where `mail` = %s;"
    cursor_drupal.execute(drupal_login, (email,))
    drupal_login_result = cursor_drupal.fetchone()
    if drupal_login_result != None:
        # check for illegal symbols
        if ('@localhost' in email) or ('__' in email):
            login = drupal_login_result['name'] \
                .replace("  ", "") \
                .replace(" ", "_") \
                .replace("@", "_") \
                .replace("__", "_") \
                .replace("-", "")
        # else:
        if email in config.RENAME_MAIL_LIST:
            login = email.split('@')[0] \
                .replace("  ", "") \
                .replace(" ", "_") \
                .replace("@", "_") \
                .replace("__", "_") \
                .replace("-", "") + str(user['id'])
            logger.info('Email found in rename list! Email: %s' % email)
        else:
            login = drupal_login_result['name']
            if not re.match('^[\w-]+$', login):
                login = email.split('@')[0]
            else:
                login = login.replace("__", "") \
                    .replace("  ", "") \
                    .replace(" ", "_") \
                    .replace("@", "_") \
                    .replace("-", "") \
                    .replace(".", "") \
                    .replace("_", "")
                login = re.sub(r'_\d\d\d\d', '', login)

        logger.info('Login: %s' % login)
    else:
        logger.error('User not found in Drupal! Email: %s\n' % email)
        continue

    # create user in discourse
    try:
        new_user = discourse.create_user(
            user['full_name'], login, email, ''.join(random.sample(string.lowercase, 12)), active='true')
        new_user_message = new_user['message']
        new_user_discourse_id = new_user['user_id']
        logger.info('%d/%s. Discourse user id: %s' % (x, len(all_useresponse_users), new_user_discourse_id))
        logger.info(new_user_message)

    except Exception, ex:
        if 'Primary email is invalid' in ex.message:
            continue

        if ('Username must be unique' in ex.message) or ('Primary email has already been taken' in ex.message):
            logger.error(ex.message, exc_info=True)
            continue

        if 'Too Many Requests' in ex.message:
            logger.error('Too Many Requests!' + ex.message, exc_info=True)
            break

        logger.warning("Unhandled error: " + ex.message, exc_info=True)
        new_user = discourse.create_user(
            user['full_name'], email.split('@')[0], email, ''.join(random.sample(string.lowercase, 8)), active='true')
        continue

    finally:
        # get discourse user_id
        list_users = discourse.list_users(type='active', filter=email)

        if list_users != None:
            discourse_id = list_users[0]['id']

        # insert line into matching table
        match_user = """
        insert into match_users
        (
            useresponse_id,
            email,
            drupal_login,
            discourse_id,
            registration_ip
        )
            values (%s, %s, %s, %s, %s)
            """
        cursor_useresponse.execute(match_user, (int(user['id']), email, login, discourse_id, reg_ip,))

        # update Discourse user with registration IP and timestamps
        query1 = """update users set registration_ip_address = %s, created_at = %s, updated_at = %s,
                    last_posted_at = %s, last_seen_at = %s where id = %s"""
        vars1 = (reg_ip, user_created_at, user_updated_at, user_last_posted_at, user_last_seen_at, discourse_id)

        query2 = "update users set registration_ip_address = %s, created_at = %s, last_seen_at = %s where id = %s"
        vars2 = (reg_ip, user_created_at, user_last_seen_at, discourse_id)

        if (not user_updated_at) or (not user_last_posted_at):
            cursor_pgsql.execute(query2, vars2)
        else:
            cursor_pgsql.execute(query1, vars1)
        conn_pgsql.commit()

    x += 1

cursor_pgsql.close()
conn_pgsql.close()

useresponse_db.commit()
useresponse_db.close()
drupal_db.close()

logger.info('Done.')
