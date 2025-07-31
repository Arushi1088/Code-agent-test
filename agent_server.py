# agent_server.py
import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, Tool

# ─── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()  # expects OPENAI_API_KEY in .env
llm = OpenAI(temperature=0)

# ─── Tools ─────────────────────────────────────────────────────────────────────
def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(args: dict) -> str:
    with open(args['path'], 'w', encoding='utf-8') as f:
        f.write(args['content'])
    return f"Wrote {len(args['content'])} characters to {args['path']}"

def run_tests(_: str) -> str:
    # adjust this to your project's test command
    proc = subprocess.run(["npm", "test"], capture_output=True, text=True)
    return proc.stdout + proc.stderr

tools = [
    Tool(
        name="read_file",
        func=lambda path: read_file(path),
        description="Reads a text file and returns its contents."
    ),
    Tool(
        name="write_file",
        func=lambda args: write_file(args),
        description="Writes content to a file. Expects a dict with 'path' and 'content'."
    ),
    Tool(
        name="run_tests",
        func=lambda _: run_tests(_),
        description="Runs the project's test suite and returns the output."
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=False
)

# ─── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins including file://

@app.route('/agent', methods=['POST'])
def handle_command():
    data = request.get_json()
    cmd = data.get("command", "").strip()
    if not cmd:
        return jsonify({"error": "No command provided"}), 400

    # Build a little script for the agent to follow:
    # 1. load the HTML
    # 2. apply the user's instruction
    # 3. write the file back out (or run tests)
    prompt = f"""
    read_file index.html
    {cmd}
    write_file
    """
    # If they asked for tests, the agent will call run_tests()
    result = agent.run(prompt)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
