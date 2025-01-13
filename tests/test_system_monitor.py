import os
from unittest.mock import MagicMock

import pytest
import tkinter as tk
from GUI.system_monitor import SystemMonitor
from db.db import create_database


@pytest.fixture(scope='function')
def db_setup():
    db_path = create_database('test.db')
    assert os.path.exists(db_path)
    yield db_path
    os.remove(db_path)

@pytest.fixture
def app(db_setup):
    root = tk.Tk()
    app = SystemMonitor(root, db_setup)
    yield app
    root.destroy()

def test_update_metrics(monkeypatch, app):
    def mock_cpu_percent(interval):
        return 50

    def mock_virtual_memory():
        return type('obj', (object,), {'percent': 30})()

    def mock_disk_usage(path):
        return type('obj', (object,), {'percent': 20})()

    monkeypatch.setattr('psutil.cpu_percent', mock_cpu_percent)
    monkeypatch.setattr('psutil.virtual_memory', mock_virtual_memory)
    monkeypatch.setattr('psutil.disk_usage', mock_disk_usage)

    app.update_metrics()

    assert app.cpu_label.cget("text") == "Загрузка ЦП: 50%"
    assert app.ram_label.cget("text") == "Использование ОЗУ: 30%"
    assert app.disk_label.cget("text") == "Использование ПЗУ: 20%"

def test_toggle_recording(app):
    app.toggle_recording()
    assert app.recording is True
    assert app.record_button.cget("text") == "Остановить запись"

    app.toggle_recording()
    assert app.recording is False
    assert app.record_button.cget("text") == "Начать запись"


def test_show_history(monkeypatch, app):
    monkeypatch.setattr('psutil.cpu_percent', lambda interval: 50)
    monkeypatch.setattr('psutil.virtual_memory', lambda: MagicMock(percent=30))
    monkeypatch.setattr('psutil.disk_usage', lambda path: MagicMock(percent=20))

    app.start_recording()
    app.update_metrics()
    app.stop_recording()

    mock_fetch_history = MagicMock(return_value=[(1, '2023-01-01 00:00:00', 50, 30, 20)])
    monkeypatch.setattr('db.db.fetch_history', mock_fetch_history)

    history_window = app.show_history()

    assert history_window.title() == 'История Записи'
    tree = history_window.children['!treeview']
    assert len(tree.get_children()) > 0

    first_item = tree.item(tree.get_children()[0])['values']

    assert isinstance(first_item, list)
    assert len(first_item) == 5
    assert isinstance(first_item[0], int)
    assert isinstance(first_item[1], str)
    assert isinstance(first_item[2], str)
    assert isinstance(first_item[3], str)
    assert isinstance(first_item[4], str)

    assert first_item[2] == '50.0'
    assert first_item[3] == '30.0'
    assert first_item[4] == '20.0'


def test_start_recording(app):
    app.start_recording()
    assert app.recording is True
    assert app.record_button.cget("text") == "Остановить запись"
    assert app.quantity_record == 0

def test_stop_recording(app):
    app.start_recording()
    app.stop_recording()
    assert app.recording is False
    assert app.record_button.cget("text") == "Начать запись"