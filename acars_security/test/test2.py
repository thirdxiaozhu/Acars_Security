import sqlite3

conn = sqlite3.connect("/home/jiaxv/inoproject/Acars_Security/src/db/b.db")
c = conn.cursor()

sql = """

    create table company(
        id int primary key not null,
        name text not null,
        age int not null,
        salary real
    )

"""

c.execute(sql)
conn.commit()
conn.close()