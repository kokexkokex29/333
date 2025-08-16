from flask import Flask, render_template
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Main page showing bot status"""
    return render_template('index.html')

@app.route('/status')
def status():
    """API endpoint for bot status"""
    return {
        'status': 'online',
        'message': 'Discord Football Bot is running!',
        'features': [
            'Club Management',
            'Player Management', 
            'Transfer System',
            'Match Scheduling',
            'Statistics & Analytics',
            'Administrative Controls'
        ]
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'discord-football-bot'}

def run_server():
    """Run the Flask web server"""
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_web_server():
    """Start the web server in a separate thread"""
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"Web server started on port {os.getenv('PORT', 5000)}")
    return server_thread
