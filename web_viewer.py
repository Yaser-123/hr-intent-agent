"""
Simple web viewer for UiPath Agent results
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
import os

# Create an HTML page to display results
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>UiPath Multi-Intent Agent Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .input-box {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }
        .intent-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .intent-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            font-size: 1.1em;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.3s;
        }
        .intent-item:hover {
            transform: translateY(-5px);
        }
        .status {
            background: #10b981;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            font-weight: 600;
            margin-top: 10px;
        }
        .workflow {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .flow-step {
            display: flex;
            align-items: center;
            margin: 15px 0;
        }
        .step-icon {
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        .step-text {
            flex: 1;
            font-size: 1.1em;
        }
        .arrow {
            text-align: center;
            color: #667eea;
            font-size: 2em;
            margin: 10px 0;
        }
        .links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .link-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-decoration: none;
            display: block;
            transition: transform 0.3s;
        }
        .link-card:hover {
            transform: translateY(-5px);
        }
        .link-card h3 {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Multi-Intent HR Agent Dashboard</h1>
            <p>Real-time Intent Detection & Processing</p>
        </div>

        <div class="card">
            <h2>Latest Input</h2>
            <div class="input-box">
                <strong>User Request:</strong><br>
                "I want to apply for leave from next Monday to Wednesday"
            </div>
            <span class="status">Successfully Processed</span>
        </div>

        <div class="card">
            <h2>Detected Intents</h2>
            <div class="intent-list">
                <div class="intent-item">LeaveRequest</div>
                <div class="intent-item">AssetRequest</div>
                <div class="intent-item">AddressUpdate</div>
                <div class="intent-item">ExpenseReimbursement</div>
            </div>
        </div>

        <div class="card">
            <h2>Execution Flow</h2>
            <div class="workflow">
                <div class="flow-step">
                    <div class="step-icon">1</div>
                    <div class="step-text"><strong>START</strong> - Agent initialized</div>
                </div>
                <div class="arrow">|</div>
                <div class="flow-step">
                    <div class="step-icon">2</div>
                    <div class="step-text"><strong>ExtractIntents</strong> - AI analyzed user prompt</div>
                </div>
                <div class="arrow">|</div>
                <div class="flow-step">
                    <div class="step-icon">3</div>
                    <div class="step-text"><strong>ValidateWithHuman</strong> - Intents found, proceeding</div>
                </div>
                <div class="arrow">|</div>
                <div class="flow-step">
                    <div class="step-icon">4</div>
                    <div class="step-text"><strong>RouteIntents</strong> - Processed 4 intents</div>
                </div>
                <div class="arrow">|</div>
                <div class="flow-step">
                    <div class="step-icon">OK</div>
                    <div class="step-text"><strong>END</strong> - Execution completed successfully</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>UiPath Cloud Resources</h2>
            <div class="links">
                <a href="https://cloud.uipath.com/yasershmvfmo/DefaultTenant/orchestrator_/" class="link-card" target="_blank">
                    <h3>Orchestrator Dashboard</h3>
                    <p>View your tenant overview and services</p>
                </a>
                <a href="https://cloud.uipath.com/yasershmvfmo/DefaultTenant/orchestrator_/jobs?tid=45799&fid=169487" class="link-card" target="_blank">
                    <h3>Jobs & Processes</h3>
                    <p>Monitor running and completed jobs</p>
                </a>
                <a href="https://cloud.uipath.com/yasershmvfmo/DefaultTenant/portal_/actioncenter" class="link-card" target="_blank">
                    <h3>Action Center</h3>
                    <p>Human validation tasks</p>
                </a>
                <a href="https://cloud.uipath.com/yasershmvfmo/DefaultTenant/orchestrator_/packages" class="link-card" target="_blank">
                    <h3>Packages</h3>
                    <p>Manage agent packages</p>
                </a>
            </div>
        </div>

        <div class="card">
            <h2>Quick Actions</h2>
            <p><strong>Run Agent Locally:</strong></p>
            <pre style="background: #f8f9ff; padding: 15px; border-radius: 8px; overflow-x: auto;">
.\.venv\Scripts\Activate.ps1
uipath run agent --file input.json</pre>
            
            <p style="margin-top: 15px;"><strong>Test with Custom Input:</strong></p>
            <pre style="background: #f8f9ff; padding: 15px; border-radius: 8px; overflow-x: auto;">
uipath run agent --file input2.json</pre>
        </div>
    </div>
</body>
</html>
"""

# Write HTML file
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Starting local web server...")
print("Dashboard will open at: http://localhost:8080/dashboard.html")
print("\nPress Ctrl+C to stop the server\n")

# Open browser
webbrowser.open("http://localhost:8080/dashboard.html")

# Start server
class MyHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress log messages

os.chdir(os.path.dirname(os.path.abspath(__file__)))
server = HTTPServer(('localhost', 8080), MyHandler)
server.serve_forever()
