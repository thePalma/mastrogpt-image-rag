import os
import vdb
import vision2 as vision
import datetime
import bucket
import base64
import re


USAGE = f"""Welcome to the Vector DB Loader.
Upload an image to insert in the DB.
"""
FORM = [
    {"label": "Load Image", "name": "pic", "required": "true", "type": "file"},
]


def upload_to_bucket(args, img):
    """Uploads the image to the bucket and returns the status."""
    bkt = bucket.Bucket(args)
    key = f"img_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    bkt.write(key, img)


def tokenize_description(text):
    # Step 1: Split into sentences using punctuation followed by space and capital letter
    sentence_end_re = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
    sentences = sentence_end_re.split(text)

    tokenized_sentences = []

    # Step 2: Tokenize each sentence
    token_pattern = re.compile(
        r"""
        \b\w+(?:[./]\w+)*\b    # words, abbreviations like U.S.A., dates like 01/22/2021
        | [’'\-–—]+            # apostrophes and dashes
        | [.,!?;:"()]+         # punctuation
        """,
        re.VERBOSE,
    )

    for sentence in sentences:
        tokens = token_pattern.findall(sentence)
        tokenized_sentences.append(" ".join(tokens))

    return tokenized_sentences


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
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"img_{timestamp}.jpg"
        encoded_img = base64.b64decode(img)

        # Insert into DB
        upload_to_bucket(args, encoded_img)

        vision_model = vision.Vision(args)
        description = vision_model.decode(img)

        # Tokenize the description
        tkn_description = tokenize_description(description)

        # Initialize vector database client
        vdb_client = vdb.VectorDB(args, "img")

        # Upload to vector database
        for desc in tkn_description:
            vdb_client.insert(key, desc)

        out = f"Image uploaded with key: {key}\nDescription: {description}"

    res["form"] = FORM
    res["output"] = out
    return res
