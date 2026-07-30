import pytest
from src.reports import Engine, ReportWriter


@pytest.fixture()
def db_engine():
    engine = Engine()
    yield engine
    engine.close()


@pytest.fixture(scope='function')
def report_writer(db_engine):
    return ReportWriter(db_engine)


def test_first_export(report_writer):
    assert report_writer.export() == "exported"


def test_final_export(report_writer):
    assert report_writer.export() == "exported"
