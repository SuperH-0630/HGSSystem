from . import args


class ConfigDatabaseRelease:
    """ MySQL 相关配置 """
    database = 'MySQL'
    mysql_url = args.p_args['mysql_url']
    mysql_name = args.p_args['mysql_name']
    mysql_passwd = args.p_args['mysql_passwd']
    mysql_port = args.p_args['mysql_port']


ConfigDatabase = ConfigDatabaseRelease
