import os
import requests as req


def test_images_rag_int():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/rag/rag"
    res = req.get(url).json()
    assert "RAG" in res.get("output", "")

    args = {"input": "@L1img a cat"}
    res = req.post(url, json=args).json()
    assert "output" in res