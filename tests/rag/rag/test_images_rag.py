import sys
import types
from unittest.mock import MagicMock
import importlib

# utility to load images_rag with mocked deps

def load_module(monkeypatch):
    bucket_inst = MagicMock()
    bucket_inst.exturl.return_value = "http://example.com/img_key"
    bucket_cls = MagicMock(return_value=bucket_inst)

    vdb_inst = MagicMock()
    vdb_inst.collection = "img"
    vdb_inst.collections = ["img"]
    
    vdb_inst.vector_search.side_effect = [
        [(0.9, "img_key", "some text about cat")],
        [(0.8, "img_key", "some text about cat")],
    ]
    vdb_cls = MagicMock(return_value=vdb_inst)

    bucket_mod = types.ModuleType("bucket")
    bucket_mod.Bucket = bucket_cls
    vdb_mod = types.ModuleType("vdb")
    vdb_mod.VectorDB = vdb_cls

    req_mod = types.ModuleType("requests")
    req_mod.post = lambda *a, **k: None

    monkeypatch.setitem(sys.modules, "bucket", bucket_mod)
    monkeypatch.setitem(sys.modules, "vdb", vdb_mod)
    monkeypatch.setitem(sys.modules, "requests", req_mod)

    sys.path.append("packages/rag/rag")
    module = importlib.import_module("images_rag")
    importlib.reload(module)

    return module, bucket_cls, bucket_inst, vdb_cls, vdb_inst


def test_parse_query_basic(monkeypatch):
    module, *_ = load_module(monkeypatch)
    res = module.parse_query("@L25img Hello")
    assert res["model"].startswith("llama")
    assert res["size"] == 25
    assert res["collection"] == "img"
    assert res["content"] == "Hello"


def test_images_rag_flow(monkeypatch):
    module, bucket_cls, bucket_inst, vdb_cls, vdb_inst = load_module(monkeypatch)

    monkeypatch.setattr(module, "llm", lambda *a, **k: "cat description")
    
    monkeypatch.setattr(module, "streamlines", lambda args, lines: "".join(lines))

    res = module.images_rag({"input": "@L5img cat"})

    bucket_cls.assert_called_once()
    assert bucket_inst.exturl.called
    assert res["html"] == "<img src='http://example.com/img_key'>"
    assert "matches the description" in res["output"]


def test_images_rag_config(monkeypatch):
    module, bucket_cls, bucket_inst, vdb_cls, vdb_inst = load_module(monkeypatch)
    monkeypatch.setattr(module, "streamlines", lambda args, lines: "".join(lines))

    res = module.images_rag({"input": "@L30img"})

    bucket_cls.assert_not_called()
    assert res["output"].startswith("model=")