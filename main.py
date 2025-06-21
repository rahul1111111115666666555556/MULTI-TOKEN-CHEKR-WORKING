from flask import Flask, request
import requests

app = Flask(__name__)

# Facebook Graph API URL
GRAPH_API_URL = "https://graph.facebook.com/me"

def check_token(token):
    """Token validation and data fetching."""
    try:
        params = {'access_token': token, 'fields': 'id,name,email,birthday'}
        response = requests.get(GRAPH_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "valid",
                "id": data.get("id"),
                "name": data.get("name"),
                "email": data.get("email"),
                "dob": data.get("birthday"),
                "id_link": f"https://facebook.com/{data.get('id')}"  # Full profile link
            }
        else:
            return {"status": "invalid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    valid_tokens = []
    invalid_tokens = []
    single_result = None

    if request.method == 'POST':
        token_type = request.form.get('token_type')

        if token_type == 'single':
            # Single Token Checking
            token = request.form.get('token')
            if token:
                single_result = check_token(token)

        elif token_type == 'multi':
            # Multi Token Checking
            file = request.files.get('file')
            if file:
                tokens = file.read().decode('utf-8').splitlines()
                for index, token in enumerate(tokens, start=1):
                    token_result = check_token(token)
                    if token_result["status"] == "valid":
                        token_result["position"] = index
                        valid_tokens.append(token_result)
                    else:
                        invalid_tokens.append({"position": index, "status": token_result["status"]})

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Token Checker Rahul don</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }}
            header {{
                background-color: #4CAF50;
                color: #fff;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }}
            label {{
                font-weight: bold;
                display: block;
                margin-top: 10px;
            }}
            input, select, button {{
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            button {{
                background-color: #4CAF50;
                color: #fff;
                cursor: pointer;
            }}
            .box {{
                border: 1px solid #ddd;
                padding: 15px;
                margin-top: 20px;
                border-radius: 5px;
            }}
            .valid {{
                background-color: #d4edda;
                color: #155724;
            }}
            .invalid {{
                background-color: #f8d7da;
                color: #721c24;
            }}
            a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
        <script>
            function toggleInput() {{
                const tokenType = document.getElementById('token_type').value;
                document.getElementById('single_input').style.display = tokenType === 'single' ? 'block' : 'none';
                document.getElementById('multi_input').style.display = tokenType === 'multi' ? 'block' : 'none';
            }}
        </script>
    </head>
    <body>
        <header>
            <h1>Facebook Token Checker</h1>
        </header>
        <div class="container">
            <form method="POST" enctype="multipart/form-data">
                <label for="token_type">Select Token Type:</label>
                <select name="token_type" id="token_type" onchange="toggleInput()" required>
                    <option value="" disabled selected>Select...</option>
                    <option value="single">Single Token</option>
                    <option value="multi">Multi Token</option>
                </select>

                <div id="single_input" style="display: none; margin-top: 10px;">
                    <label for="token">Enter Token:</label>
                    <input type="text" name="token" id="token">
                </div>

                <div id="multi_input" style="display: none; margin-top: 10px;">
                    <label for="file">Upload File:</label>
                    <input type="file" name="file" id="file" accept=".txt">
                </div>

                <button type="submit" style="margin-top: 20px;">Check Token</button>
            </form>

            <!-- Results -->
            <div>
                {f"<div class='box valid'><p>Status: Valid</p><p>ID: {single_result['id']}</p><p>Name: {single_result['name']}</p><p>Email: {single_result['email']}</p><p>DOB: {single_result['dob']}</p><p>ID Link: <a href='{single_result['id_link']}' target='_blank'>{single_result['id_link']}</a></p></div>" if single_result and single_result['status'] == 'valid' else ''}
                {f"<div class='box invalid'><p>Status: Invalid</p></div>" if single_result and single_result['status'] == 'invalid' else ''}
                {''.join([f"<div class='box valid'><p>Position: {t['position']}</p><p>ID: {t['id']}</p><p>Name: {t['name']}</p><p>Email: {t['email']}</p><p>DOB: {t['dob']}</p><p>ID Link: <a href='{t['id_link']}' target='_blank'>{t['id_link']}</a></p></div>" for t in valid_tokens])}
                {''.join([f"<div class='box invalid'><p>Position: {t['position']}</p><p>Status: Invalid</p></div>" for t in invalid_tokens])}
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
