import sqlite3
from tinydb import TinyDB
from tqdm import tqdm


def createTable(_recordList):
    recordList: list[tuple] = []
    for record in tqdm(_recordList):
        # print(record.keys())
        record: tuple[str, str, str] = (record['Addr'], record['Name'], str(record['Code']))
        recordList.append(record)
    del _recordList
    try:
        sqliteConnection = sqlite3.connect('contStore.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        # cursor.execute("CREATE TABLE cont(address, name, bytecode)")

        sqlite_insert_query = """INSERT INTO cont
                            (address, name, bytecode) 
                            VALUES (?, ?, ?);"""
        print("Inserting multiple records into cont table ...")
        cursor.executemany(sqlite_insert_query, recordList)
        print("Total", cursor.rowcount, "Records inserted successfully into cont table")
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.OperationalError as e:
        raise e
    except sqlite3.Error as error:
        print("Failed to insert multiple records into sqlite table\n", error)
        raise(error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


if __name__ == '__main__':
    print("starting")
    db = TinyDB('./src/contracts.json')
    print("Loading in DB")
    db = db.all()
    print("DB loaded")
    createTable(db)