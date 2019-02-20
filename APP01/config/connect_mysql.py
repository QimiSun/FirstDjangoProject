import pymysql


def conn_MySQL(host, port, user, password, database, charset="utf8"):
    db = pymysql.Connect(host=host,
                             port=port,
                             user=user,
                             password=password,
                             database=database,
                             charset=charset
                             )
    return db