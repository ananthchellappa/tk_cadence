import re
from pathlib import Path

import pytest

from transcript import TranscriptLogger, next_free_path


def test_next_free_path_returns_base_when_not_existing(tmp_path):
    base = tmp_path / "CDS.log"
    assert next_free_path(base) == base


def test_next_free_path_appends_dot_one_when_base_exists(tmp_path):
    base = tmp_path / "CDS.log"
    base.write_text("")
    assert next_free_path(base) == tmp_path / "CDS.log.1"


def test_next_free_path_walks_past_existing_iterations(tmp_path):
    base = tmp_path / "CDS.log"
    base.write_text("")
    (tmp_path / "CDS.log.1").write_text("")
    (tmp_path / "CDS.log.2").write_text("")
    assert next_free_path(base) == tmp_path / "CDS.log.3"


def test_next_free_path_skips_only_actual_existing(tmp_path):
    base = tmp_path / "CDS.log"
    base.write_text("")
    (tmp_path / "CDS.log.2").write_text("")  # gap at .1
    # Algorithm picks the smallest unused >= 1, which is .1.
    assert next_free_path(base) == tmp_path / "CDS.log.1"


def test_logger_writes_timestamped_line(tmp_path):
    path = tmp_path / "CDS.log"
    log = TranscriptLogger(path)
    log.record("INPUT", "print('hi')")
    log.close()
    content = path.read_text()
    assert re.match(
        r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] INPUT: print\('hi'\)\n$",
        content,
    )


def test_logger_appends_multiple_records(tmp_path):
    path = tmp_path / "CDS.log"
    log = TranscriptLogger(path)
    log.record("INPUT", "a")
    log.record("OUTPUT", "b")
    log.record("MENU", "File > Exit")
    log.close()
    lines = path.read_text().splitlines()
    assert len(lines) == 3
    assert lines[0].endswith("INPUT: a")
    assert lines[1].endswith("OUTPUT: b")
    assert lines[2].endswith("MENU: File > Exit")


def test_logger_line_buffered_persists_before_close(tmp_path):
    path = tmp_path / "CDS.log"
    log = TranscriptLogger(path)
    log.record("INPUT", "early")
    # Read while still open — line buffering must have flushed.
    content = path.read_text()
    assert "INPUT: early" in content
    log.close()


def test_logger_close_is_idempotent(tmp_path):
    log = TranscriptLogger(tmp_path / "CDS.log")
    log.close()
    log.close()  # should not raise


def test_logger_appends_to_preexisting_file(tmp_path):
    path = tmp_path / "CDS.log"
    path.write_text("# preserved\n")
    log = TranscriptLogger(path)
    log.record("INPUT", "x")
    log.close()
    content = path.read_text()
    assert content.startswith("# preserved\n")
    assert "INPUT: x" in content


def test_logger_path_attribute_matches_constructor(tmp_path):
    path = tmp_path / "CDS.log"
    log = TranscriptLogger(path)
    assert log.path == path
    log.close()


def test_record_after_close_raises(tmp_path):
    log = TranscriptLogger(tmp_path / "CDS.log")
    log.close()
    with pytest.raises(ValueError):
        log.record("INPUT", "too late")
