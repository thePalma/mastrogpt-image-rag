import sys
import vdb
import vision2 as vision
import datetime
import bucket
import base64

USAGE = f"""Welcome to the Vector DB Loader.
Upload an image to insert in the DB.
"""
FORM = [
  {
    "label": "Load Image",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

def upload_to_bucket(args, img):
    """Uploads the image to the bucket and returns the status."""
    bkt = bucket.Bucket(args)
    key = f"img_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    bkt.write(key, img)

def upload_to_vdb(args, key, description):
    """Uploads the image to the vector database and returns the status."""
    vdb_client = vdb.VectorDB(args, "img")
    vdb_client.insert(key, description)
  
def images_loader(args):
    res = {}
    out = USAGE
    inp = args.get("input", "")

    if type(inp) is dict and "form" in inp:
        img = inp.get("form", {}).get("pic", "")
        print(f"uploaded size {len(img)}")

        # Generate image description
        vision_model = vision.Vision(args)
        description = vision_model.decode(img)

        # Generate unique key
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        key = f"img_{timestamp}.jpg"
        encoded_img = base64.b64decode(img)

        # Insert into DB
        status = upload_to_bucket(args, encoded_img)
        
        vision_model = vision.Vision(args)
        description = vision_model.decode(img)

        upload_to_vdb(args, key, description)
        out = f"Image uploaded with key: {key}\nDescription: {description}"

    res['form'] = FORM
    res["output"] = out
    return res