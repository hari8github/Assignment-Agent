from flask import Flask, render_template, request, jsonify, send_file
from main import create_enhanced_assignment
import os, json
from docx import Document
from reportlab.pdfgen import canvas

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_assignment():
    try:
        data = request.get_json()
        topic = data.get("topic")
        print("Received topic:", topic)  # 👈 Add this
        if not topic:
            return jsonify({"error": "No topic provided."}), 400

        result = create_enhanced_assignment(topic)
        output = result.get("output")
        print("Output:", output)  # 👈 Add this
        return jsonify(result if output is None else json.loads(output))

    except Exception as e:
        print("Backend error:", e)  # 👈 Add this too
        return jsonify({"error": str(e)}), 500

@app.route("/download/<format>")
def download_assignment(format):
    filename = f"assignment.{format}"
    filepath = os.path.join(os.getcwd(), filename)

    if not os.path.exists("assignment.txt"):
        return jsonify({"error": "Please generate the assignment first."}), 404

    # Read base assignment
    with open("assignment.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # Generate file based on requested format
    if format == "txt":
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    elif format == "pdf":
        c = canvas.Canvas(filepath)
        y = 800
        for line in content.splitlines():
            c.drawString(50, y, line[:120])
            y -= 15
            if y < 50:
                c.showPage()
                y = 800
        c.save()

    elif format == "docx":
        doc = Document()
        for line in content.splitlines():
            doc.add_paragraph(line)
        doc.save(filepath)

    else:
        return jsonify({"error": "Unsupported format"}), 400

    return send_file(filepath, as_attachment=True)

@app.route("/download-edited", methods=["POST"])
def download_edited():
    data = request.get_json()
    format = data.get("format")
    topic = data.get("title", "Assignment")
    intro = data.get("introduction", "")
    conclusion = data.get("conclusion", "")
    sections = data.get("sections", [])

    content = f"# {topic}\n\nIntroduction\n\n{intro}\n\n"
    for i, section in enumerate(sections, 1):
        content += f"## {i}. {section['title']}\n\n{section['content']}\n\n"
    content += f"## Conclusion\n\n{conclusion}\n"

    filename = f"assignment.{format}"
    filepath = os.path.join(os.getcwd(), filename)

    if format == "txt":
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    elif format == "pdf":
        c = canvas.Canvas(filepath)
        y = 800
        for line in content.splitlines():
            c.drawString(50, y, line[:120])
            y -= 15
            if y < 50:
                c.showPage()
                y = 800
        c.save()
    elif format == "docx":
        doc = Document()
        for line in content.splitlines():
            doc.add_paragraph(line)
        doc.save(filepath)
    else:
        return jsonify({"error": "Unsupported format"}), 400

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)