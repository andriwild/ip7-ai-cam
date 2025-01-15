from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def receive_post_request():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        print("Received data:", data)
        
        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
