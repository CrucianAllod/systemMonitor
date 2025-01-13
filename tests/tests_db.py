import os
import pytest
import sqlite3
from db.db import create_database, insert_load_data, fetch_history

@pytest.fixture(scope='function')
def setup_database():
    db_path = create_database('test.db')
    assert os.path.exists(db_path)
    yield db_path
    os.remove(db_path)


def test_create_database(setup_database):
    connection = sqlite3.connect(setup_database)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SystemLoad';")
    table_exists = cursor.fetchone() is not None
    connection.close()
    assert table_exists

def test_insert_load_data(setup_database):
    insert_load_data(50.0, 30.0, 20.0, setup_database)
    connection = sqlite3.connect(setup_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM SystemLoad ORDER BY id DESC LIMIT 1;")
    records = cursor.fetchall()
    connection.close()

    assert len(records) == 1
    assert records[0][2] == 50.0
    assert records[0][3] == 30.0
    assert records[0][4] == 20.0

def test_fetch_history(setup_database):
    insert_load_data(50.0, 30.0, 20.0, setup_database)
    insert_load_data(60.0, 40.0, 30.0, setup_database)

    history = fetch_history(2, setup_database)

    print(history)

    assert len(history) == 2
    assert history[0][2] == 50.0
    assert history[1][2] == 60.0