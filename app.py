import io
import base64
import time
from flask import Flask, request, jsonify, render_template
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__)

MODEL = "u2net"
MAX_SIDE = 1024
_session = None


def get_session():
    global _session
    if _session is None:
        t0 = time.time()
        _session = new_session(MODEL)
        print(f"[调试] 模型加载耗时: {time.time() - t0:.2f}s")
    return _session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/remove", methods=["POST"])
def api_remove():
    if "image" not in request.files:
        return jsonify({"ok": False, "msg": "没有收到图片"}), 400

    file = request.files["image"]
    try:
        t0 = time.time()
        img = Image.open(file.stream).convert("RGBA")
        orig_size = img.size

        # 限尺寸
        if max(img.size) > MAX_SIDE:
            ratio = MAX_SIDE / max(img.size)
            img = img.resize(
                (int(img.width * ratio), int(img.height * ratio)),
                Image.LANCZOS,
            )

        session = get_session()
        result = remove(img, session=session)

        # 还原尺寸
        if result.size != orig_size:
            result = result.resize(orig_size, Image.LANCZOS)

        # 转 base64 返回
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        return jsonify({
            "ok": True,
            "image": f"data:image/png;base64,{b64}",
            "elapsed": round(time.time() - t0, 2),
            "size": orig_size,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "msg": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)