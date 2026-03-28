
from flask import Flask, render_template, request, send_file
import os
from my_utils import speech_to_text, analyze_text 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

pdf_path = "report.pdf"

def generate_pdf(analysis, text, question):
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Interview Feedback Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Question: {question}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Transcript:", styles["Heading2"]))
    content.append(Paragraph(text, styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Final Score: {analysis['final_score']}/100", styles["Normal"]))
    content.append(Paragraph(f"Relevance: {analysis['relevance']}%", styles["Normal"]))
    content.append(Paragraph(f"Confidence: {analysis['confidence']}%", styles["Normal"]))
    content.append(Paragraph(f"Clarity: {analysis['clarity']}%", styles["Normal"]))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Feedback:", styles["Heading2"]))

    for f in analysis["feedback"]:
        content.append(Paragraph(f"- {f}", styles["Normal"]))

    doc.build(content)


@app.route("/download")
def download():
    return send_file(pdf_path, as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    analysis = None
    question = ""
    manual_text = ""

    if request.method == "POST":
      question = request.form.get("question") or ""
      manual_text = request.form.get("manual_text")

    file = request.files.get("audio")

    if manual_text:
        text = manual_text
        analysis = analyze_text(text, question)
        generate_pdf(analysis, text, question)

    elif file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        text = speech_to_text(filepath)

        if text:
            analysis = analyze_text(text, question)
            generate_pdf(analysis, text, question)

    return render_template("index.html", text=text, analysis=analysis, question=question)


if __name__ == "__main__":
    app.run(debug=True)