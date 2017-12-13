-- update site settings
update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'autohighlight_all_code';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'autohighlight_all_code', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'autohighlight_all_code');

update site_settings set data_type = 8, value = 'apache|bash|cs|cpp|css|coffeescript|diff|xml|http|ini|json|java|javascript|makefile|markdown|nginx|objectivec|ruby|perl|php|python|sql|handlebars|groovy|gradle|scala|kotlin', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'highlighted_languages';
insert into site_settings (data_type, value, name, created_at, updated_at) select 8, 'apache|bash|cs|cpp|css|coffeescript|diff|xml|http|ini|json|java|javascript|makefile|markdown|nginx|objectivec|ruby|perl|php|python|sql|handlebars|groovy|gradle|scala|kotlin','highlighted_languages', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'highlighted_languages');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'disable_digest_emails';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'disable_digest_emails', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'disable_digest_emails');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'show_topic_featured_link_in_digest';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'show_topic_featured_link_in_digest', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'show_topic_featured_link_in_digest');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'disable_emails';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'disable_emails', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'disable_emails');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'strip_images_from_short_emails';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'strip_images_from_short_emails', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'strip_images_from_short_emails');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'unsubscribe_via_email_footer';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'unsubscribe_via_email_footer', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'unsubscribe_via_email_footer');

update site_settings set data_type = 3, value = 10240, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_image_size_kb';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 10240, 'max_image_size_kb', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_image_size_kb');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'send_welcome_message';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'send_welcome_message', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'send_welcome_message');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'has_login_hint';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'has_login_hint', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'has_login_hint');

update site_settings set data_type = 7, value = '1', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'default_trust_level';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, '1', 'default_trust_level', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'default_trust_level');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'bootstrap_mode_enabled';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'bootstrap_mode_enabled', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'bootstrap_mode_enabled');

update site_settings set data_type = 8, value = 'categories|latest|new|unread|top', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'top_menu';
insert into site_settings (data_type, value, name, created_at, updated_at) select 8, 'categories|latest|new|unread|top', 'top_menu', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'top_menu');

update site_settings set data_type = 7, value = 'apple', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'emoji_set';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, 'apple', 'emoji_set', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'emoji_set');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_user_locale';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'allow_user_locale', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_user_locale');

update site_settings set data_type = 1, value = '/discuss/', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'long_polling_base_url';
insert into site_settings (data_type, value, name, created_at, updated_at) select 1, '/discuss/', 'long_polling_base_url', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'long_polling_base_url');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'fixed_category_positions';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'fixed_category_positions', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'fixed_category_positions');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'fixed_category_positions_on_create';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'fixed_category_positions_on_create', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'fixed_category_positions_on_create');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'enable_whispers';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'enable_whispers', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'enable_whispers');

update site_settings set data_type = 7, value = 'bar', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'category_style';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, 'bar', 'category_style', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'category_style');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'email_editable';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'email_editable', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'email_editable');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'verbose_sso_logging';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'verbose_sso_logging', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'verbose_sso_logging');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'sso_overrides_email';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'sso_overrides_email', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'sso_overrides_email');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'enable_sso';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'enable_sso', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'enable_sso');

update site_settings set data_type = 8, value = 'admin|moderator|administrator|mod|sys|system|community|info|you|name|username|user|nickname|discourse|discourseorg|discourseforum|support|account-created|cuba', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'reserved_usernames';
insert into site_settings (data_type, value, name, created_at, updated_at) select 8, 'admin|moderator|administrator|mod|sys|system|community|info|you|name|username|user|nickname|discourse|discourseorg|discourseforum|support|account-created|cuba', 'reserved_usernames', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'reserved_usernames');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_username_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'max_username_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_username_length');

update site_settings set data_type = 3, value = 8, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_password_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 8, 'min_password_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_password_length');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_post_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'min_post_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_post_length');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_first_post_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'min_first_post_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_first_post_length');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'title_min_entropy';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'title_min_entropy', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_min_entropy');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_topic_title_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'min_topic_title_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_topic_title_length');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'body_min_entropy';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, '2', 'body_min_entropy', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'body_min_entropy');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_uncategorized_topics';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'allow_uncategorized_topics', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_uncategorized_topics');

update site_settings set data_type = 3, value = 8, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_title_similar_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 8, 'min_title_similar_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_title_similar_length');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'display_name_on_posts';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'display_name_on_posts', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'display_name_on_posts');

update site_settings set data_type = 3, value = 102400, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_attachment_size_kb';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 102400, 'max_attachment_size_kb', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_attachment_size_kb');

update site_settings set data_type = 8, value = 'jpg|jpeg|png|gif|txt|log|err|zip|tar|gz|7z|xml|xls|xlsx|doc|docx|java|js|jar|pdf|PDF|rar|gradle|groovy|csv|htm|html|mov|rtf|rb|pom|md|py|sh|bat|cmd|svg', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'authorized_extensions';
insert into site_settings (data_type, value, name, created_at, updated_at) select 8, 'jpg|jpeg|png|gif|txt|log|err|zip|tar|gz|7z|xml|xls|xlsx|doc|docx|java|js|jar|pdf|PDF|rar|gradle|groovy|csv|htm|html|mov|rtf|rb|pom|md|py|sh|bat|cmd|svg', 'authorized_extensions', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'authorized_extensions');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_uploaded_avatars';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'allow_uploaded_avatars', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_uploaded_avatars');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_restore';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'allow_restore', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_restore');

update site_settings set data_type = 3, value = 15, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'maximum_backups';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 15, 'maximum_backups', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'maximum_backups');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'disable_avatar_education_message';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'disable_avatar_education_message', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'disable_avatar_education_message');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'new_version_emails';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'new_version_emails', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'new_version_emails');

update site_settings set data_type = 7, value = '0', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'default_email_digest_frequency';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, '0', 'default_email_digest_frequency', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'default_email_digest_frequency');

update site_settings set data_type = 3, value = 0, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_user_api_reqs_per_day';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 0, 'max_user_api_reqs_per_day', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_user_api_reqs_per_day');

update site_settings set data_type = 3, value = 0, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_user_api_reqs_per_minute';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 0, 'max_user_api_reqs_per_minute', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_user_api_reqs_per_minute');

update site_settings set data_type = 8, value = 'discourse://auth_redirect', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allowed_user_api_auth_redirects';
insert into site_settings (data_type, value, name, created_at, updated_at) select 8, 'discourse://auth_redirect', 'allowed_user_api_auth_redirects', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allowed_user_api_auth_redirects');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'show_filter_by_tag';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'show_filter_by_tag', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'show_filter_by_tag');

update site_settings set data_type = 3, value = 7, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_tags_per_topic';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 7, 'max_tags_per_topic', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_tags_per_topic');

update site_settings set data_type = 7, value = 'box', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'tag_style';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, 'box', 'tag_style', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'tag_style');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'tagging_enabled';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'tagging_enabled', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'tagging_enabled');

update site_settings set data_type = 7, value = '4', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_trust_to_create_tag';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, '4', 'min_trust_to_create_tag', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_trust_to_create_tag');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'assign_enabled';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'assign_enabled', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'assign_enabled');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'disable_discourse_narrative_bot_welcome_post';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'disable_discourse_narrative_bot_welcome_post', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'disable_discourse_narrative_bot_welcome_post');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'discourse_narrative_bot_disable_public_replies';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'discourse_narrative_bot_disable_public_replies', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'discourse_narrative_bot_disable_public_replies');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'daily_performance_report';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'daily_performance_report', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'daily_performance_report');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'assigns_public';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'assigns_public', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'assigns_public');

update site_settings set data_type = 3, value = 60, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'max_username_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 60, 'max_username_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'max_username_length');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'min_username_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'min_username_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'min_username_length');

update site_settings set data_type = 3, value = 136, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'read_time_word_count';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 136, 'read_time_word_count', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'read_time_word_count');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_duplicate_topic_titles';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 't', 'allow_duplicate_topic_titles', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_duplicate_topic_titles');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'newuser_max_images';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'newuser_max_images', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'newuser_max_images');

update site_settings set data_type = 3, value = 2, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'newuser_max_attachments';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 2, 'newuser_max_attachments', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'newuser_max_attachments');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'title_prettify';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'title_prettify', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_prettify');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'allow_uppercase_posts';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'allow_uppercase_posts', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'allow_uppercase_posts');

update site_settings set data_type = 5, value = 'f', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'title_fancy_entities';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 'f', 'title_fancy_entities', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_fancy_entities');

update site_settings set data_type = 3, value = 60, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'title_max_word_length';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 60, 'title_max_word_length', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_max_word_length');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'staff_notes_enabled';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'staff_notes_enabled', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'staff_notes_enabled');

update site_settings set data_type = 3, value = 5, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'topic_views_heat_high';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 5, 'topic_views_heat_high', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_max_word_length');

update site_settings set data_type = 3, value = 10, created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'summary_posts_required';
insert into site_settings (data_type, value, name, created_at, updated_at) select 3, 10, 'summary_posts_required', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'title_max_word_length');

update site_settings set data_type = 5, value = 't', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'default_email_always';
insert into site_settings (data_type, value, name, created_at, updated_at) select 5, 't', 'default_email_always', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'staff_notes_enabled');

update site_settings set data_type = 7, value = 'Strict', created_at = LOCALTIMESTAMP, updated_at = LOCALTIMESTAMP where name = 'same_site_cookies';
insert into site_settings (data_type, value, name, created_at, updated_at) select 7, 'Strict', 'same_site_cookies', LOCALTIMESTAMP, LOCALTIMESTAMP where not exists (select 1 from site_settings where name = 'staff_notes_enabled');

commit;