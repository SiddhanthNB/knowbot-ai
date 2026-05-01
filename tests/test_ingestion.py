import lib.pipeline.ingestion as wikipedia


def test_load_topics_reads_flat_list_from_yaml(monkeypatch, tmp_path):
    topics_file = tmp_path / "topics.yaml"
    topics_file.write_text("topics:\n  - Topic A\n  - Topic B\n", encoding="utf-8")
    monkeypatch.setattr(wikipedia, "TOPICS_FILE", topics_file)

    assert wikipedia._load_topics() == ["Topic A", "Topic B"]
