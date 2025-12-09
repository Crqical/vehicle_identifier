import os
import json
from flask import (
    Flask, request, redirect, url_for,
    render_template_string, send_from_directory, abort
)

# --- PATHS ---

PICTURES_DIR = "picture"
MASTER_JSON = "pictures.json"
LABELS_DIR = "labels"

os.makedirs(LABELS_DIR, exist_ok=True)

app = Flask(__name__)


# --- HELPERS ---

def load_master_pictures():
    """Load all picture metadata from pictures.json."""
    if not os.path.exists(MASTER_JSON):
        return []

    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # New format: dict with "pictures"
    if isinstance(data, dict) and "pictures" in data:
        return data["pictures"]

    # Old format: list directly
    if isinstance(data, list):
        return data

    return []


def get_descriptions():
    pics = load_master_pictures()
    return sorted({p.get("description") for p in pics if p.get("description")})


def labels_path_for_description(desc: str) -> str:
    # Just in case, strip path separators
    safe_desc = desc.replace(os.sep, "_")
    return os.path.join(LABELS_DIR, f"{safe_desc}_labels.json")


def load_labels_for_description(desc: str):
    path = labels_path_for_description(desc)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_labels_for_description(desc: str, labels):
    path = labels_path_for_description(desc)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)


def find_next_unlabeled_picture(desc: str):
    """Return the next picture dict for this description that has not been labeled yet."""
    pictures = [p for p in load_master_pictures() if p.get("description") == desc]
    labels = load_labels_for_description(desc)
    labeled_filenames = {l.get("filename") for l in labels}

    for p in pictures:
        if p.get("filename") not in labeled_filenames:
            return p, len(pictures), len(labels)
    return None, len(pictures), len(labels)


# --- HTML TEMPLATES (inline to keep single-file) ---

INDEX_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Car Labeling - Select Description</title>
  </head>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h1>Select a description / camera</h1>

    {% if descriptions %}
      {% for desc in descriptions %}
        <form method="get" action="{{ url_for('label', description=desc) }}" style="margin: 6px 0;">
          <button type="submit" style="padding: 8px 14px; font-size: 14px;">
            {{ desc }}
          </button>
        </form>
      {% endfor %}
    {% else %}
      <p>No descriptions found. Check your pictures.json file.</p>
    {% endif %}
  </body>
</html>
"""

LABEL_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Label {{ description }}</title>
  </head>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h1>{{ description }}</h1>
    <p>
      File: <strong>{{ picture.filename }}</strong><br>
      Index: {{ picture.index }}<br>
      Taken: {{ picture.date }} {{ picture.time }}<br>
      Description total index: {{ picture.description_total }}<br>
      Labeled: {{ labeled_count }} / {{ total_count }}
    </p>

    <div style="margin: 15px 0;">
      <img src="{{ url_for('image', description=description, filename=picture.filename) }}"
           style="max-width:90%; max-height:80vh; border:1px solid #ccc;">
    </div>

    {% if error_message %}
      <p style="color:red;">{{ error_message }}</p>
    {% endif %}

    <form method="post" action="{{ url_for('submit', description=description) }}">
      <input type="hidden" name="filename" value="{{ picture.filename }}">
      <input type="hidden" name="index" value="{{ picture.index }}">
      <input type="hidden" name="date" value="{{ picture.date }}">
      <input type="hidden" name="time" value="{{ picture.time }}">
      <input type="hidden" name="description_total" value="{{ picture.description_total }}">

      <label for="car_amount">How many cars are in this picture?</label><br>
      <input type="number" id="car_amount" name="car_amount" min="0" style="margin-top:4px; padding:4px; width:80px;">

      <div style="margin-top:10px;">
        <button type="submit" name="action" value="submit" style="padding:6px 12px; margin-right:8px;">
          Submit
        </button>
        <button type="submit" name="action" value="issue" style="padding:6px 12px;">
          Issue (unreadable / black / hard to see)
        </button>
      </div>
    </form>

    <p style="margin-top:20px;">
      <a href="{{ url_for('index') }}">Back to descriptions</a>
    </p>
  </body>
</html>
"""

DONE_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ description }} - Done</title>
  </head>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h1>{{ description }}</h1>
    <p>No more pictures to label for this description.</p>
    <p><a href="{{ url_for('index') }}">Back to descriptions</a></p>
  </body>
</html>
"""


# --- ROUTES ---

@app.route("/")
def index():
    descriptions = get_descriptions()
    return render_template_string(INDEX_HTML, descriptions=descriptions)


@app.route("/label/<description>")
def label(description):
    picture, total_count, labeled_count = find_next_unlabeled_picture(description)
    if picture is None:
        # No more pictures
        return render_template_string(
            DONE_HTML,
            description=description
        )

    # Make sure description_total exists to avoid KeyError
    if "description_total" not in picture:
        picture["description_total"] = 0

    return render_template_string(
        LABEL_HTML,
        description=description,
        picture=picture,
        total_count=total_count,
        labeled_count=labeled_count,
        error_message=None
    )


@app.route("/submit/<description>", methods=["POST"])
def submit(description):
    action = request.form.get("action")
    filename = request.form.get("filename")
    index = int(request.form.get("index"))
    date = request.form.get("date")
    time_ = request.form.get("time")
    description_total = int(request.form.get("description_total"))

    labels = load_labels_for_description(description)

    if action == "issue":
        error = "YES"
        car_amount = None
    else:
        car_text = (request.form.get("car_amount") or "").strip()
        if not car_text.isdigit():
            # Re-show same picture with error message
            picture = {
                "filename": filename,
                "index": index,
                "date": date,
                "time": time_,
                "description_total": description_total
            }
            # need total and labeled counts for display
            all_pics = [p for p in load_master_pictures() if p.get("description") == description]
            total_count = len(all_pics)
            labeled_count = len(labels)
            return render_template_string(
                LABEL_HTML,
                description=description,
                picture=picture,
                total_count=total_count,
                labeled_count=labeled_count,
                error_message="Please enter a number for car amount (or use Issue if unreadable)."
            )
        car_amount = int(car_text)
        error = "NO"

    # Build label entry for this picture
    entry = {
        "index": index,
        "filename": filename,
        "date": date,
        "time": time_,
        "description": description,
        "description_total": description_total,
        "error": error,
        "car_amount": car_amount
    }
    labels.append(entry)
    save_labels_for_description(description, labels)

    # Move on to next picture
    return redirect(url_for("label", description=description))


@app.route("/image/<description>/<filename>")
def image(description, filename):
    """
    Serve images. First tries inside picture/<description>/, then fallback to picture/ root
    (in case you didn't run the organize script).
    """
    subdir = os.path.join(PICTURES_DIR, description)
    path1 = os.path.join(subdir, filename)
    path2 = os.path.join(PICTURES_DIR, filename)

    if os.path.exists(path1):
        return send_from_directory(subdir, filename)
    elif os.path.exists(path2):
        return send_from_directory(PICTURES_DIR, filename)
    else:
        abort(404)


if __name__ == "__main__":
    # Bind to 0.0.0.0 for Replit compatibility
    app.run(host="0.0.0.0", port=5000, debug=True)
