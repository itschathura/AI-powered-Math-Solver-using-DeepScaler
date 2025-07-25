import ollama
import gradio as gr
import re

# Function to clean output
def clean_output(text):
    # Remove tags like <think> or <step>
    text = re.sub(r'<[^>]+>', '', text)
    # Remove LaTeX block commands like \boxed{...}
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    # Remove other LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Remove LaTeX dollar signs
    text = re.sub(r'\${1,2}', '', text)
    # Keep essential math symbols (= and /), remove others
    text = re.sub(r'[\^*±→∞√≤≥≠•→←⇒↔×÷]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Function to get solution from Ollama
def solve_math_problem(problem):
    response = ollama.chat(
        model='deepscaler',
        messages=[
            {'role': 'system', 'content': 'Always answer clearly and briefly in English. Use simple math formatting. Avoid unnecessary LaTeX or explanation.'},
            {'role': 'user', 'content': problem}
        ]
    )
    raw_output = response['message']['content']
    return clean_output(raw_output)

# Define Gradio UI
interface = gr.Interface(
    fn=solve_math_problem,
    inputs=gr.Textbox(label="Chat here"),
    outputs=gr.Textbox(label="Solution"),
    title="AI-powered Math Solver",
    description="Ask any math question, and Deepscaler will provide a cleaned, step-by-step solution.",
    article="""
    <p style='text-align: center; font-size: 14px; color: gray;'>
        Developed by <b>Chathura Mahesh</b>
    </p>
    """
)

# Launch the app
interface.launch()
