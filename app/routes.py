from flask import Blueprint, render_template, request, send_file
import tensorflow as tf
from utils.preprocess import preprocess_input
from utils.pdf_generator import generate_pdf
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
import uuid

main = Blueprint('main', __name__)

MODELS = {
    "cnn": tf.keras.models.load_model("models/cnn_model.h5"),
    "cnn_lstm": tf.keras.models.load_model("models/cnn_lstm_model.h5")
}

temp_model = None
@main.route("/", methods=["GET", "POST"])
def index():
    results = []
    plots = []
    selected_model = None
    if request.method == "POST":
        files = request.files.getlist("file") # allows multiple files
        model_choice = request.form.get("model")
        selected_model = model_choice
        model = MODELS.get(selected_model)
        temp_model = model
        if model is None:
            return render_template("index.html", result="Error: Invalid model selection.", results=[], plots=[])
        
        for file in files:
            filename = file.filename
            temp_path = f"temp_{uuid.uuid4().hex}.csv"
            file.save(temp_path)
            try:
                X = preprocess_input(temp_path)  # Reshapes to (1, 3197, 1)
                prob = model.predict(X)[0][0]
                prediction = "🚀 Likely Exoplanet!" if prob > 0.5 else "🪐 No exoplanet transit detected."
                confidence = f"{(prob * 100):.2f}%" if prob > 0.5 else f"{(100 - prob * 100):.2f}%"

                # Plot using raw (unscaled) data
                raw_df = pd.read_csv(temp_path, header=None)
                raw_data = raw_df.iloc[0].values  # for PDF plotting
                trace = go.Scatter(y=raw_data, mode='lines', name='Flux')
                layout = go.Layout(title=f"Light Curve: {filename}", height=300)
                fig = go.Figure(data=[trace], layout=layout)
                plot_html = pio.to_html(fig, full_html=False)

                results.append({
                    "filename": filename,
                    "prediction": prediction,
                    "confidence": confidence,
                    "raw_data": raw_data.tolist()
                })
                plots.append(plot_html)

            except Exception as e:
                results.append({
                    "filename": filename,
                    "prediction": f"❌ Error processing file: {e}",
                    "confidence": "-"
                })
                plots.append("")

            finally:
                os.remove(temp_path)

        # Generate downloadable pdf
        pdf_buf = generate_pdf(results, temp_model)
        request.pdf_buf=pdf_buf # storing in request for use in download route

    return render_template("index.html", results=results, plots=plots, model_selected=selected_model)

@main.route("/download-pdf", methods=["POST"])
def download_pdf():
    # Reconstruct PDF from posted result data
    results = []
    filenames = request.form.getlist("filename[]")
    predictions = request.form.getlist("prediction[]")
    confidences = request.form.getlist("confidence[]")

    for f, p, c in zip(filenames, predictions, confidences):
        results.append({"filename": f, "prediction": p, "confidence": c})

    model_used = request.form.get("model_used", "Unknown model")
    pdf_buf = generate_pdf(results, model_name=model_used)
    return send_file(pdf_buf, download_name="Exoplanet_Report.pdf", as_attachment=True)
