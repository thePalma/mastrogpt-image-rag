import sys
import types
import base64
from unittest.mock import MagicMock
import importlib

# Helper to load module with stubbed dependencies

def load_module(monkeypatch):
    bucket_inst = MagicMock()
    bucket_cls = MagicMock(return_value=bucket_inst)

    vdb_inst = MagicMock()
    vdb_cls = MagicMock(return_value=vdb_inst)

    vision_inst = MagicMock()
    vision_inst.decode.return_value = "A cat sits on a mat."
    vision_cls = MagicMock(return_value=vision_inst)

    bucket_mod = types.ModuleType("bucket")
    bucket_mod.Bucket = bucket_cls
    vdb_mod = types.ModuleType("vdb")
    vdb_mod.VectorDB = vdb_cls
    vision_mod = types.ModuleType("vision2")
    vision_mod.Vision = vision_cls

    monkeypatch.setitem(sys.modules, "bucket", bucket_mod)
    monkeypatch.setitem(sys.modules, "vdb", vdb_mod)
    monkeypatch.setitem(sys.modules, "vision2", vision_mod)

    sys.path.append("packages/rag/loader")
    module = importlib.import_module("images_loader")
    importlib.reload(module)

    return module, bucket_cls, bucket_inst, vdb_cls, vdb_inst, vision_cls, vision_inst


def test_tokenize_description(monkeypatch):
    module, *_ = load_module(monkeypatch)
    text = "Hello world. My name is John! What is U.S.A.? 01/22/2021 is a date"
    tokens = module.tokenize_description(text)
    assert tokens == [
        "Hello world .",
        "My name is John !",
        "What is U.S.A .? 01/22/2021 is a date",
    ]


def test_images_loader_upload(monkeypatch):
    module, bucket_cls, bucket_inst, vdb_cls, vdb_inst, vision_cls, vision_inst = load_module(monkeypatch)

    # fixed timestamp
    class FakeDateTime(module.datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return module.datetime.datetime(2024, 1, 1, 0, 0, 0)
    monkeypatch.setattr(module.datetime, "datetime", FakeDateTime)

    encoded = base64.b64encode(b"data").decode()
    args = {"input": {"form": {"pic": encoded}}}

    res = module.images_loader(args)

    expected_key = "img_20240101000000.jpg"
    bucket_cls.assert_called_once_with(args)
    bucket_inst.write.assert_called_once_with(expected_key, b"data")

    vdb_cls.assert_called_once_with(args, "img")
    # number of inserts equals number of tokenized sentences
    assert vdb_inst.insert.call_count == len(module.tokenize_description("A cat sits on a mat."))

    assert expected_key in res["output"]
    assert "A cat sits on a mat." in res["output"]
    assert res["form"] == module.FORM


def test_images_loader_no_input(monkeypatch):
    module, bucket_cls, bucket_inst, vdb_cls, vdb_inst, _, _ = load_module(monkeypatch)

    res = module.images_loader({})
    assert res["output"].startswith(module.USAGE.splitlines()[0])
    # ensure no external calls
    bucket_cls.assert_not_called()
    vdb_cls.assert_not_called()