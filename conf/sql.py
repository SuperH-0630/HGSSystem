from . import args


class ConfigDatabaseRelease:
    database = 'MySQL'
    mysql_url = args.p_args['mysql_url']
    mysql_name = args.p_args['mysql_name']
    mysql_passwd = args.p_args['mysql_passwd']
    mysql_port = args.p_args['mysql_port'] if (args.p_args['mysql_port'] is not None and
                                               len(args.p_args['mysql_port']) > 0) else None


ConfigDatabase = ConfigDatabaseRelease
