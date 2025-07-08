import os, re, requests as req
import json, socket, traceback, time
import vdb
import bucket

MODELS = {"P": "phi4:14b", "L": "llama3.1:8b", "M": "mistral:latest"}

USAGE = """
This is a RAG (Retrieval-Augmented Generation) service for images.
You can use it to search for images based on text queries.
Start with `@[LPM][<size>]` to select the model then add `<size>` sentences from the context.
Models: L=llama P=phi4 M=mistral.
Your query is then passed to the LLM with the sentences to generate a better description.
Example: `@L30 What is the image of a cat?`
The RAG than searches for images in the `img` collection and returns the first image that matches the description provided by the LLM.
"""

# Pattern: @<model><size><collection> <optional content>
PATTERN = re.compile(r"^@([LPDM]?)(\d*)(\w*)(\s*.*)$")


def parse_query(content):
    res = {"model": MODELS["L"], "size": 30, "collection": "img", "content": content}

    match = PATTERN.match(content.strip())
    if not match:
        return res

    model_key, size_str, collection, content = match.groups()

    if model_key in MODELS:
        res["model"] = MODELS[model_key]

    try:
        size = int(size_str)
        res["size"] = size
    except:
        pass

    res["content"] = content.strip()

    return res


def streamlines(args, lines):
    sock = args.get("STREAM_HOST")
    port = int(args.get("STREAM_PORT") or "0")
    out = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if sock:
            s.connect((sock, port))
        try:
            for line in lines:
                time.sleep(0.1)
                msg = {"output": line}
                # print(msg)
                out += line
                if sock:
                    s.sendall(json.dumps(msg).encode("utf-8"))
        except Exception as e:
            traceback.print_exc(e)
            out = str(e)
        if sock:
            s.close()
    return out


def stream(args, lines):
    sock = args.get("STREAM_HOST")
    port = int(args.get("STREAM_PORT") or "0")
    out = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if sock:
            s.connect((sock, port))
        try:
            for line in lines:
                dec = json.loads(line.decode("utf-8")).get("response")
                msg = {"output": dec}
                # print(msg)
                out += dec
                if sock:
                    s.sendall(json.dumps(msg).encode("utf-8"))
        except Exception as e:
            traceback.print_exc(e)
            out = str(e)
        if sock:
            s.close()
    return out


def llm(args, model, prompt):
    host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
    auth = args.get("AUTH", os.getenv("AUTH"))
    url = f"https://{auth}@{host}/api/generate"

    msg = {"model": model, "prompt": prompt, "stream": True}

    lines = req.post(url, json=msg, stream=True).iter_lines()
    return stream(args, lines)


def images_rag(args):
    inp = str(args.get("input", ""))
    out = USAGE
    res = {}
    res["streaming"] = False

    if inp != "":
        opt = parse_query(inp)
        if opt["content"] == "":
            db = vdb.VectorDB(args, opt["collection"])
            lines = [
                f"model={opt['model']}\n",
                f"size={opt['size']}\n",
                f"collection={db.collection}\n",
                f"({",".join(db.collections)})",
            ]
            out = streamlines(args, lines)
        else:
            db = vdb.VectorDB(args, opt["collection"])
            db_res = db.vector_search(opt["content"], limit=opt["size"])
            prompt = ""
            if len(db_res) > 0:
                prompt += "Consider the following text:\n"
                for w, key, text in db_res:
                    prompt += f"{text}\n"
                prompt += "Generate an image description for the following prompt:\n"
                prompt += f"{opt['content']}"
                print("prompt: ", prompt)
                llm_out = llm(args, opt["model"], prompt)
                out = llm_out

                db_res = db.vector_search(llm_out, limit=opt["size"])
                bkt = bucket.Bucket(args)
                img_key = db_res[0][1]
                img = bkt.exturl(img_key, 3600)
                if img:
                    res["html"] = f"<img src='{img}'>"
                    out += "\n\nHere is an image that matches the description."
    res["output"] = out
    return res
