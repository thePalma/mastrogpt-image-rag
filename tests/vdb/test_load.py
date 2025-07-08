import sys
sys.path.append("packages/vdb/load")
import vdb, time

def test_vdb():
    args = {}

    collection = "pytest"
    db = vdb.VectorDB(args, collection)
    db.destroy(collection)
    db.setup(collection)
    assert len(db.embed("hello world")) == 1024

    assert len(db.vector_search("hello")) == 0
    
    db.insert("Hello world", "Hello world")
    db.insert("This is a test", "This is a test")
    db.insert("This is another test", "This is another test")
    time.sleep(1)

    test = db.vector_search("test")
    assert len(test) == 3
    assert test[0][2].find("test") != -1

    hello = db.vector_search("hello")
    assert hello[0][2].find("Hello") != -1

    assert db.remove_by_substring("test") == 2
    




