import gradio as gr
import requests
import base64
import os

uploaded_image_path = None  # Global state

def handle_upload(file):
    global uploaded_image_path
    if file:
        uploaded_image_path = file
        return "Image uploaded!"
    return "Upload failed."

def query_llava(user_msg, history):
    global uploaded_image_path

    url = "http://localhost:11434/api/generate"

    images = None
    if uploaded_image_path and os.path.exists(uploaded_image_path):
        with open(uploaded_image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
            images = [img_b64]

    prompt = user_msg.strip()
    if not prompt and not images:
        return "Please enter a math question or upload an image."

    payload = {
        "model": "llava-llama3",
        "prompt": prompt,
        "stream": False
    }
    if images:
        payload["images"] = images

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        uploaded_image_path = None
        return data.get("response", "No response from model.")
    except Exception as e:
        return f"Error: {e}"

# Custom CSS
custom_css = """
.gradio-container {
    width: 900px !important;
    margin: 0 auto !important;
}
#upload-icon input[type='file'] {
    display: none;
}
#upload-icon label {
    cursor: pointer;
    font-size: 22px;
    margin-left: 10px;
}
#custom-chat-input {
    display: flex;
    align-items: center;
}
.footer-text {
    text-align: center;
    margin-top: 10px;
    font-size: 13px;
    color: #888;
    font-style: italic;
}
"""

with gr.Blocks(css=custom_css) as app:
    gr.Markdown("AI-Powered Math Solver V2.0")
    
    chatbot = gr.Chatbot()
    state = gr.State([])

    with gr.Row(elem_id="custom-chat-input"):
        user_input = gr.Textbox(placeholder="Type your math question...", scale=10, lines=1, show_label=False)
        image_file = gr.File(label="", file_types=["image"], visible=False)
        image_status = gr.Textbox(visible=False)

        gr.HTML("""
            <div id="upload-icon">
                <label for="camera-upload">📷</label>
                <input id="camera-upload" type="file" accept="image/*" />
            </div>
            <script>
                const input = document.getElementById('camera-upload');
                input.addEventListener('change', function() {
                    if (input.files.length > 0) {
                        gradioApp().querySelector('input[type=file]').files = input.files;
                        gradioApp().querySelector('input[type=file]').dispatchEvent(new Event('change'));
                    }
                });
            </script>
        """)

    submit_btn = gr.Button("Submit")
    
    def handle_submit(message, history):
        response = query_llava(message, history)
        history.append((message, response))
        return "", history

    user_input.submit(handle_submit, [user_input, state], [user_input, chatbot])
    submit_btn.click(handle_submit, [user_input, state], [user_input, chatbot])
    image_file.upload(handle_upload, inputs=image_file, outputs=image_status)

    gr.Markdown("<div class='footer-text'>Developed by Chathura Dharmasiri</div>")

if __name__ == "__main__":
    app.launch(share=True)
