from . import args


class ConfigDatabaseRelease:
    database = 'MySQL'
    mysql_url = args.p_args.mysql_url[0]
    mysql_name = args.p_args.mysql_name[0]
    mysql_passwd = args.p_args.mysql_passwd[0]
    mysql_port = args.p_args.mysql_port[0]


ConfigDatabase = ConfigDatabaseRelease
