# Migration UseResponse forum to Discourse

**Requires Python 2.7**

This bundle of scripts is designed to migrate from UseResponse forum with Drupal authorization to Discourse platform. As a result, new forum will work with the same Drupal using SSO.

Forum operates from subfolder **/discuss** and uses an external database.

There are tw oway to migrate.
1. The process on local machine may take up to 2 hours.
2. Network migration takes 5-6 hours (less secure, slow, not recommended).

## Requirements
1. Python 2.7
2. Direct access to all databases: Drupal mysql, UseResponse mysql and Discourse pgsql. The advantage is to use local mysql databases, both Drupal and UseResponse.
3. Access to old attachments.
4. English Discourse locale is used during migration (for proper error handling).
In case of SSO integration to Drupal later:
5. Drupal discourse_sso plugin installed.
6. Clean URLs enabled in Drupal.

## Disclaimer
This instruction and files are provided **as is**. Use it on your own risk.

## Disclaimer for Russian users
Because of scripts handle English error messages, therefore it is recommended to deploy English Discourse first, then perform a migration and at the end switch forum language via app.yml and rebuild:

    LANG: ru_RU.UTF-8
    DISCOURSE_DEFAULT_LOCALE: ru

## Usage
### Install Discourse
Install and setup Discourse forum using the instruction below: https://github.com/discourse/discourse/blob/master/docs/INSTALL-cloud.md (~40 min).

Ensure that your Discourse instance works. Then follow next steps configuring external database and subfolder.

### Install Postgres
Install packages:
```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo -i -u postgres
psql
```
Setup database:
```
CREATE USER username PASSWORD 'password';
CREATE DATABASE discourse OWNER discourse;
\c discourse CREATE EXTENSION hstore;
CREATE EXTENSION pg_trgm;
ALTER USER username WITH SUPERUSER;
```

### Install Python
Install packages:
```
sudo apt install python-pip
pip install --upgrade pip
sudo pip install psycopg2
sudo apt-get install libmysqlclient-dev
sudo pip install MySQL-python
sudo pip install pydiscourse
sudo pip install humanize
```

### Setup Discourse
Edit `/var/discourse/containers/app.yml`, follow next steps.

#### Disable docker database
Comment the line:
```
# "templates/postgres.template.yml"
```

#### Set version tag
To use tag from Discourse source code, uncomment the following line (stable is highly recommended):
```
version: v1.9.0.beta11
```

#### Forum hostname
Define server hostname, developer email:
```
DISCOURSE_HOSTNAME: <YOUR_SERVER_NAME_HERE>
DISCOURSE_DEVELOPER_EMAILS: '<EMAIL>'
```

#### External database
Add database definition to **env** section:
```
DISCOURSE_DB_USERNAME: username
DISCOURSE_DB_PASSWORD: password
DISCOURSE_DB_HOST: 127.0.0.1
DISCOURSE_DB_NAME: discourse
DISCOURSE_DB_PORT: 5432
```

#### Plugins
Add necessary plugins to **hooks** section:
```
hooks:
  after_code:
    - exec:
        cd: $home/plugins
        cmd:
          - git clone https://github.com/discourse/docker_manager.git
          - git clone https://github.com/discourse/discourse-assign.git
          - git clone https://github.com/discourse/discourse-solved.git
          - git clone https://github.com/gdpelican/retort.git
          - git clone https://github.com/discourse/discourse-staff-notes.git
          - git clone https://github.com/discourse/discourse-tooltips.git
```

#### Subfolder
To run forum from a subfolder, define `DISCOURSE_RELATIVE_URL_ROOT` and copy the following code to **run** section:
```
DISCOURSE_RELATIVE_URL_ROOT: /discuss
```
Do not end the line with slash `/`!

`Run` section should look like this:
```
run:
    - exec:
        cd: $home
        cmd:
          - mkdir -p public/discuss
          - cd public/discuss && ln -s ../uploads && ln -s ../backups
    - replace:
       global: true
       filename: /etc/nginx/conf.d/discourse.conf
       from: proxy_pass http://discourse;
       to: |
          rewrite ^/(.*)$ /discuss/$1 break;
          proxy_pass http://discourse;
    - replace:
       filename: /etc/nginx/conf.d/discourse.conf
       from: etag off;
       to: |
          etag off;
          location /discuss/ {
             rewrite ^/discuss/?(.*)$ /$1;
          }
    - replace:
       filename: /etc/nginx/conf.d/discourse.conf
       from: etag off;
       to: |
          etag off;
          location /discuss {
             rewrite ^/discuss/?(.*)$ /$1;
          }
    - replace:
         filename: /etc/nginx/conf.d/discourse.conf
         from: $proxy_add_x_forwarded_for
         to: $http_fastly_client_ip
         global: true
    - exec:
         cmd:
           - sed -i '/no-referrer-when-downgrade/a proxy_redirect https:\/\/<YOUR_SERVER_NAME_HERE>\/ https:\/\/<YOUR_SERVER_NAME_HERE>\/discuss\/;' /etc/nginx/conf.d/discourse.conf
           - sed -i '/no-referrer-when-downgrade/a proxy_redirect https:\/\/<YOUR_SERVER_NAME_HERE>\/discuss\/ https:\/\/<YOUR_SERVER_NAME_HERE>\/discuss\/;' /etc/nginx/conf.d/discourse.conf
           - sed -i '/no-referrer-when-downgrade/a proxy_redirect https:\/\/<YOUR_SERVER_NAME_HERE>\/discourse_sso https:\/\/<YOUR_SERVER_NAME_HERE>\/discourse_sso;' /etc/nginx/conf.d/discourse.conf
           - sed -i 's/client_max_body_size 10m ;/client_max_body_size 100m ;/g' /etc/nginx/conf.d/discourse.conf
```
where **client_max_body_size 100m** must be greater than your largest attachment filesize on old forum.

#### Real IP address
If your forum is located behind a proxy, add the following lines to your proxy...:

    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $http_fastly_client_ip;
    proxy_set_header X-Forwarded-Proto $thescheme;

...and remove these lines from `app.yml` (add to **run** section after last **sed** this code):

           - sed -i '/proxy_set_header X-Real-IP $remote_addr;/d' /etc/nginx/conf.d/discourse.conf
           - sed -i '/proxy_set_header X-Forwarded-For $http_fastly_client_ip;/d' /etc/nginx/conf.d/discourse.conf
           - sed -i '/proxy_set_header X-Forwarded-Proto $thescheme;/d' /etc/nginx/conf.d/discourse.conf

#### API rate limits
During installation you may have increased limits. It is not enough to set higher values in Discourse site settings. Add the following code to `app.yml` to increase limits up to 1000 times. Return values back after migration.

           - sed -i 's/limit_conn connperip 20/limit_conn connperip 20000/g' /etc/nginx/conf.d/discourse.conf
           - sed -i 's/limit_req zone=flood burst=12/limit_req zone=flood burst=12000/g' /etc/nginx/conf.d/discourse.conf
           - sed -i 's/limit_req zone=bot burst=100/limit_req zone=bot burst=100000/g' /etc/nginx/conf.d/discourse.conf

Or temporary modify file:  `/var/discourse/templates/web.ratelimited.template.yml`

#### Zoom images
To activate Lightbox (zoom images), add to the end of app.yml file:
```
docker_args:
    - "--add-host=<FQDN>:127.0.0.1"
    - "--add-host=<HOSTNAME>:127.0.0.1"
```

### Rebuild Discourse
Rebuild your instance using command:
```
/var/discourse/launcher rebuild app --docker-args --net=host --skip-mac-address
```
`--net=host --skip-mac-address` keys are necessary for subfolder docker configuration.

#### Add admin account
Create an admin account.
```
/var/discourse/launcher enter app
rails c
u = User.create!(username: "forum-admin", email: "forum-admin@example.com", password: "pass", admin: true)
u.activate
exit
```

#### Add API access key
Log in using Discourse admin account, generate an API access key for user `system`. Use it in `config.py` later.

#### Get client_id
Using web browser console, get the `client_id`: first open topic creation dialog, then try to attach a picture. Find in console the following line:
`.../discuss/uploads.json?client_id=94c9a530cd5d4186a598558615083928&authenticity_token=...`

At the same time you may follow the same `client_id` in
`/var/discourse/shared/standalone/log/rails/production.log` as "client_id"=>"94c9a530cd5d4186a598558615083928".

Use it in `config.py` later.

#### Update site settings
Set custom values to forum settings, for ex. disable email sending etc (~20 min), then **rebuild it**.

    update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'disable_emails';
    insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'disable_emails', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'disable_emails');

    update site_settings set data_type = 1, value = '/discuss/', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'long_polling_base_url';
    insert into site_settings (data_type, value, name, created_at, updated_at) select 1, '/discuss/', 'long_polling_base_url', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'long_polling_base_url');

You may run `update-site-settings.sql` as well.

Now perform the **rebuild**.

### Migration
#### Prepare config for migration
Copy `config_template.py` to `config.py` and fill the following params in `config.py` file (~15 min):
```
# Drupal database
#
DRUPAL_DATABASE_HOST = 'localhost'                      // hostname
DRUPAL_DATABASE_PORT = 6033                             // port
DRUPAL_DATABASE_NAME = 'drupal'                         // name
DRUPAL_DATABASE_LOGIN = 'root'                          // login
DRUPAL_DATABASE_PASSWORD = 'root'                       // password
#
# Useresponse database
#
USERESPONSE_DATABASE_HOST = 'localhost'                 // hostname
USERESPONSE_DATABASE_PORT = 6033                        // port
USERESPONSE_DATABASE_NAME = 'useresponse'               // name
USERESPONSE_DATABASE_LOGIN = 'root'                     // login
USERESPONSE_DATABASE_PASSWORD = 'root'                  // password
#
# Discourse server
#
DISCOURSE_BASE_URL = "https://<FQDN>"                   // forum URL (in case of local migration, use "http://localhost")
DISCOURSE_FOLDER = "discuss"                            // forum subfolder
DISCOURSE_LOGIN = "login"                               // admin login
DISCOURSE_API_KEY = "abcdef123456abcdef123456"          // API access key
DISCOURSE_CLIENT_ID = "94c9a530cd5d4186a598558615083928"
DISCOURSE_DATABASE_HOST = "<FQDN>"                      // database hostname
DISCOURSE_DATABASE_PORT = 5432                          // database port (external)
DISCOURSE_DATABASE_NAME = "discourse"                   // database name
DISCOURSE_DATABASE_LOGIN = "root"                       // database login
DISCOURSE_DATABASE_PASSWORD = "root"                    // database password
#
# Logger
#
LOG_LEVEL = 'INFO'                                      // logger verbosity level
#
# Stop list
#
STOP_MAIL_LIST = [
    'lorem@example.com'                                  // mail list separated by comma
]                                                        // for users who no need to migrate
#
# Rename emails
#
RENAME_EMAIL_LIST = [
  'lorem@example.com'                                    // mail list separated by comma
]                                                        // for emails need to rename
#
# Exclude topics
#
EXCLUDE_TOPIC_LIST = [
    'Lorem ipsum'                                         // exclude topics, separated by comma,
]                                                         // that no need to migrate.
]

STOP_TITLE_LIST = [
    'Lorem ipsum'                                         // exclude topic titles, separated by comma,
]                                                         // that no need to fix cyrillic slugs.
```
#### Prepare source forum
##### Stop forum
Stop source UseResponse forum and clone both Drupal and UseResponse databases to Discourse server, prior to local migration. Network migration may be too slow.

##### Prepare attachments
Tar or rsync source attachments to destination.

#### Migrate users
**Requirements:**
1. API access key
2. Min username length: 2
3. Max username length: 60
4. Alphanumeric name set rules (single underscore allowed)

*check forum settings before run!*

Run `python discourse_create_users.py` (~30 min for 1k users, over network, 10 min locally).

    python discourse_create_users.py

Create a backup using Discourse backup tool.

##### Add administrators
Add administrators using shell:
```
/var/discourse/launcher enter app
rake admin:invite[admin@example.com]
```

#### Migrate topics
**Requirements:**
1. API access key
2. Max body length < 32000
3. Old internal URLs in body convert to /discuss/t
4. Old markdown and bbcode syntax convert to markdown
5. allow uppercase posts = yes
6. title prettify = no
7. title fancy entities = no
8. title max word length = 60
9. min post length = 2
10. min first post length = 2
11. min topic title length = 2

*check forum settings before run!*

Current script supports sorting topics by categories during migration. If you need sorting, ensure that categories has been created:
`Announcements`, `Support`, `Ideas`, `Site Feedback`, `General Discussion`

Run `python discourse_create_topics.py` (~6-30 min for 3k topics).

    python discourse_create_topics.py

Create a backup.

#### Migrate comments (posts)
**Requirements:**
1. API access key
2. Maximum body length < 32000
3. Old internal URLs in body convert to /discuss/t
4. Old markdown and bbcode syntax convert to markdown
5. allow uppercase posts = yes
6. title prettify = no
7. title fancy entities = no
8. title max word length = 60
9. min post length = 2

*check forum settings before run!*

Run `python discourse_create_comments.py` (~15-30 min for 9k posts).

    python discourse_create_comments.py

Create a backup.

#### Change owner
In source mysql run:
```
set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
set session sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
```
This is required before changing objects ownership.

Run `python discourse_change_owner.py` (~1 min).

    python discourse_change_owner.py

Create a backup.

#### Migrate attachments
**Requirements:**
1. max attachment size > your largest attachment
2. max image size kb = 10240
3. check nginx `client_max_body_size`

*check forum settings before run!*
```
    /var/discourse/launcher enter app
    grep max_body /etc/nginx/conf.d/discourse.conf
```
it should return current value of max allowed filesize to be uploaded through nginx. It must be greater than your largest attachment file (it can be tuned in `app.yml` at the beginning).

Run `python discourse_create_attachments.py` (~60 min for 1.5k files over network).

    python discourse_create_attachments.py

Create full backup using Discourse backup tool.

#### Migrate likes
##### Migrate topics likes
This script allows running multiple times.

Run `python discourse_create_topic_votes.py`

    python discourse_create_topic_votes.py

##### Migrate posts likes
Run `python discourse_create_post_votes.py`

    python discourse_create_post_votes.py

Create full backup.

#### Update topic timestamps
Update last posted message time in the Discourse database:
```
update topics set last_posted_at = created_at where last_posted_at is NULL;
update topics set updated_at = last_posted_at, bumped_at = last_posted_at;
update posts set updated_at = created_at, last_version_at = created_at, baked_at = created_at;
commit;
```
Navigate to Latest page. Hover the number of posts at the right. Check the time in the hint, it should be real.

Create full backup.

#### Update user activity
Run `python discourse_update_user_stats.py`

    python discourse_update_user_stats.py

### Post installation tasks
Perform necessary steps to return some site settings to defaults (limits, emailing etc)

### SSO
If you continue using Drupal, follow SSO setup here: https://meta.discourse.org/t/trouble-connecting-drupal-and-discourse/34168/7 or https://meta.discourse.org/t/trouble-connecting-drupal-and-discourse/34168/8

Done.
