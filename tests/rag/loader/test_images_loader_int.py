import os
import base64
import pathlib
import requests as req


def test_images_loader_int():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/rag/loader"
    # call without parameters just to retrieve the form structure
    res = req.get(url).json()
    assert any(field.get("name") == "pic" for field in res.get("form", []))

    img = base64.b64encode(pathlib.Path("tests/vision/cat.jpg").read_bytes()).decode()
    args = {"input": {"form": {"pic": img}}}
    res = req.post(url, json=args).json()
    assert "Image uploaded" in res.get("output", "")