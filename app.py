from github_agent_server import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
