from fpdf import FPDF
import io
import os

from flask import current_app

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 12, "🪐 Exoplanet Detection Report", ln=True, align='C', fill=True)
        self.ln(5)
        

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.set_text_color(150)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')

def generate_pdf(results, model_name):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Register fonts
    font_path_1 = os.path.join(current_app.root_path, "static", "fonts", "DejaVuSans.ttf")
    font_path_2 = os.path.join(current_app.root_path, "static", "fonts", "DejaVuSans-Bold.ttf")
    pdf.add_font("DejaVu", "", font_path_1, uni=True)
    pdf.add_font("DejaVu", "B", font_path_2, uni=True )

    pdf.add_page()
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 10, f"Model Used: {model_name}", ln=True)
    pdf.ln(5)

    exoplanet_count = 0
    total = len(results)

    for r in results:
        filename = r.get("filename", "Unknown")
        prediction = r.get("prediction", "N/A")
        confidence_str = r.get("confidence", "0")

        if isinstance(confidence_str, str) and confidence_str.endswith('%'):
            confidence = float(confidence_str.strip('%'))
        else:
            confidence = float(confidence_str)

        if "Likely Exoplanet" in prediction:
            exoplanet_count += 1

        # Section Box Header
        pdf.set_fill_color(240, 240, 255)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, f"📄 {filename}", ln=True, fill=True)
        pdf.set_font("DejaVu", size=11)
        pdf.cell(0, 10, f"Prediction: {prediction}", ln=True)
        pdf.cell(0, 10, f"Confidence: {confidence:.2f}%", ln=True)

        # Light curve visualization
        # if "raw_data" in r:
        #     try:
        #         fig = go.Figure()
        #         fig.add_trace(go.Scatter(y=r["raw_data"], mode="lines", line=dict(color="royalblue")))
        #         fig.update_layout(title="Light Curve", height=300, margin=dict(t=40, b=40, l=10, r=10))

        #         img_path = f"temp_plot_{uuid.uuid4().hex}.png"
        #         fig.write_image(img_path, width=600, height=300)
        #         pdf.image(img_path, w=170)
        #         os.remove(img_path)
        #     except Exception as e:
        #         pdf.set_text_color(255, 0, 0)
        #         pdf.multi_cell(0, 8, f"⚠️ Could not generate plot.\n{str(e)}")
        #         pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

    # Summary Page
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_fill_color(230, 255, 230)
    pdf.cell(0, 12, "📊 Evaluation Summary", ln=True, fill=True)
    pdf.ln(5)

    pdf.set_font("DejaVu", size=12)
    #pdf.cell(0, 10, f"Total Files Processed: {total}", ln=True)
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(70, 10, "Filename", 1, 0, 'C', True)
    pdf.cell(70, 10, "Prediction", 1, 0, 'C', True)
    pdf.cell(40, 10, "Confidence", 1, 1, 'C', True)

    pdf.set_font("DejaVu", size=10)
    for r in results:
        pdf.cell(70, 10, r["filename"], 1)
        pdf.cell(70, 10, r["prediction"], 1)
        pdf.cell(40, 10, str(r["confidence"]), 1, 1)

    pdf.cell(0, 10, f"Predicted Exoplanets: {exoplanet_count}", ln=True)
    pdf.cell(0, 10, f"Predicted Non-Exoplanets: {total - exoplanet_count}", ln=True)
    pdf.cell(0, 10, f"Model Used: {model_name}", ln=True)

    # Final conclusion box
    pdf.ln(15)
    pdf.set_fill_color(255, 250, 200)
    pdf.set_font("DejaVu", "B", 12)
    pdf.multi_cell(0, 10, f"🧠 Conclusion:\nBased on the above results, "
                          f"the model '{model_name}' flagged {exoplanet_count} file(s) as potential exoplanets.", fill=True)

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
