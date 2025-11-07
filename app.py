import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

# 【這就是修改的地方】
# 告訴 Flask，模板檔案就在和 app.py 相同的目錄
app = Flask(__name__, template_folder='.')
CORS(app)

# 從環境變數中讀取 Ollama API 的 URL
OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434')

# 路由：渲染主頁面
@app.route('/')
def home():
    # 現在 render_template 會直接在根目錄找到 index.html
    return render_template('index.html')

# 路由：處理聊天請求
@app.route('/chat', methods=['POST'])
def chat():
    user_data = request.json
    if not user_data or 'prompt' not in user_data:
        return jsonify({"error": "Prompt is missing"}), 400
    prompt_base = """
    你現在是一個聊天機器人，請根據使用者的輸入進行回覆。
    請使用英文回覆使用者的問題。
    請注意，請勿在回覆中提及你是由 Ollama 提供支援的。
    請保持回覆的簡潔與明確。
    請以友善且專業的語氣進行回覆。
    """
    prompt_final = prompt_base + user_data['prompt']
    model = user_data.get('model', 'llama3.2')

    try:
        payload = {
            "model": model,
            "prompt": prompt_final,
            "stream": False
        }
        response = requests.post(f"{OLLAMA_API_URL}/api/generate", json=payload)
        response.raise_for_status()
        response_data = response.json()
        return jsonify({"response": response_data.get('response', 'No response content.')})

    except requests.exceptions.RequestException as e:
        error_message = f"無法連接到 Ollama API ({OLLAMA_API_URL})。請確認您已在主機上執行 'ollama serve'，並且 Docker 的網路設定正確。"
        print(f"錯誤: {e}")
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
