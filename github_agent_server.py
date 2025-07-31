# github_agent_server.py - Simplified GitHub Integration v2
import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from github import Github

# Load environment variables
load_dotenv()
gh = Github(os.getenv("GITHUB_TOKEN"))

# Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

def modify_github_file(command):
    """Modify the index.html file on GitHub based on command"""
    try:
        # Get the repository
        repo = gh.get_repo("Arushi1088/Code-agent-test")
        
        # Get current file content
        file_content = repo.get_contents("index.html")
        current_content = file_content.decoded_content.decode('utf-8')
        
        # Apply modifications based on command
        updated_content = current_content
        cmd = command.lower()
        
        # Color changes - improved logic
        if "red" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #DC3545;', updated_content)
        elif "green" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #28A745;', updated_content)
        elif "blue" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #007BFF;', updated_content)
        elif "yellow" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #FFC107;', updated_content)
        elif "purple" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #6F42C1;', updated_content)
        elif "orange" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #FD7E14;', updated_content)
        elif "pink" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #E91E63;', updated_content)
        
        # Size changes
        if "larger" in cmd or "bigger" in cmd:
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 20px 40px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 24px;', updated_content)
        elif "smaller" in cmd or "tiny" in cmd:
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 8px 16px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 14px;', updated_content)
        
        # Text changes
        if "hello world" in cmd or ("hello" in cmd and "world" in cmd):
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Hello World</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Hello World</title>', updated_content)
        elif "click me" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Click Me</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Click Me</title>', updated_content)
        elif "submit" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Submit</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Submit</title>', updated_content)
        
        # Shape changes
        if "rounded" in cmd or "round" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 25px;', updated_content)
        elif "square" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 0px;', updated_content)
        
        # Check if content actually changed, but proceed anyway for user feedback
        content_changed = updated_content != current_content
        
        if content_changed:
            # Update the file on GitHub
            repo.update_file(
                path="index.html",
                message=f"Agent update: {command}",
                content=updated_content,
                sha=file_content.sha
            )
            
            # Also update the local file
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return f"✅ Successfully updated both GitHub repo and local file with: {command}"
        else:
            # Even if no change, give positive feedback
            color_map = {
                "red": "#DC3545", "green": "#28A745", "blue": "#007BFF", 
                "yellow": "#FFC107", "purple": "#6F42C1", "orange": "#FD7E14", "pink": "#E91E63"
            }
            
            for color, hex_code in color_map.items():
                if color in cmd and hex_code in current_content:
                    return f"✅ Button is already {color}! Try a different color like: blue, green, purple, yellow, orange, pink"
            
            return f"✅ Processed command: {command}. Try: 'make it blue', 'make it larger', 'hello world'"
        
    except Exception as e:
        return f"❌ Error updating GitHub: {str(e)}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/agent', methods=['POST'])
def handle_command():
    data = request.get_json()
    cmd = data.get("command", "").strip()
    
    if not cmd:
        return jsonify({"error": "Please provide a command"}), 400
    
    result = modify_github_file(cmd)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
