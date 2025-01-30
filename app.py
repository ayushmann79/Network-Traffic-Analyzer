from flask import Flask, jsonify, render_template
import psutil
import time
from threading import Thread
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable cross-origin resource sharing

# Global variables to store network stats
network_stats = {
    "bytes_recv": 0,
    "download_speed": 0,
    "bytes_sent": 0,
    "upload_speed": 0,
}

# Function to format byte sizes into human-readable formats
size_units = ['bytes', 'KB', 'MB', 'GB', 'TB']

def format_size(bytes):
    for unit in size_units:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024


# Function to monitor network stats in the background
def monitor_network():
    global network_stats

    prev_stats = psutil.net_io_counters()
    prev_sent = prev_stats.bytes_sent
    prev_recv = prev_stats.bytes_recv

    while True:
        time.sleep(1)
        current_stats = psutil.net_io_counters()

        # Calculate download and upload speeds
        download_speed = current_stats.bytes_recv - prev_recv
        upload_speed = current_stats.bytes_sent - prev_sent

        # Update global network stats
        network_stats = {
            "bytes_recv": current_stats.bytes_recv,
            "download_speed": download_speed,
            "bytes_sent": current_stats.bytes_sent,
            "upload_speed": upload_speed,
        }

        prev_sent = current_stats.bytes_sent
        prev_recv = current_stats.bytes_recv


# Start monitoring network stats in a separate thread
thread = Thread(target=monitor_network)
thread.daemon = True
thread.start()

@app.route("/api/network-stats")
def get_network_stats():
    # Return network stats as JSON
    return jsonify({
        "bytes_recv": format_size(network_stats["bytes_recv"]),
        "download_speed": f"{format_size(network_stats['download_speed'])}/s",
        "bytes_sent": format_size(network_stats["bytes_sent"]),
        "upload_speed": f"{format_size(network_stats['upload_speed'])}/s",
    })

@app.route("/")
def index():
    # Render the frontend HTML
    return render_template("index.html")

if __name__ == "__main__":
    # Bind to the IP address you want (192.168.56.1)
    app.run(debug=True, host='192.168.56.1', port=5000)  # Replace with your desired IP
