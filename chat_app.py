
from flask import Flask, render_template, request, session
from flask_caching import Cache
from flask import jsonify
import atexit
import sys
import os

current_file_path = os.path.abspath(__file__)
root_folder = os.path.dirname(current_file_path)
sys.path.append(root_folder)


from source.chat_backend import ChatBackend
from source.security import get_sessions

app = Flask(__name__)
app.secret_key = 'your_secret_key'

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 0
}
app.config.from_mapping(config)
cache = Cache(app)

# dictionary to store cb object
cb_obj = {}

# Function to delete the object
def cleanup():
    global cache
    cb = cb_obj.get("cb")
    del cb    
    del cache

# Register delete_object function to be called when the application exits
atexit.register(cleanup)

chat_filename = 'chat.html'
login_filename = 'login.html'

@app.route("/")
def home():    
    return render_template(login_filename)

@app.route("/chat.html")
def chat():
    return render_template(chat_filename)

@app.route("/session_names")
def get_session_names():    
    data = get_sessions()
    return jsonify(data)

@app.route("/set_session")
def set_session():
    session_name = request.args.get('session')  
    print("Session Name:", session_name) 
    session['session'] = session_name
    cb = ChatBackend(cache)
    cb_obj["cb"] = cb
    #return redirect(url_for('chat'))
    return "/chat.html"

@app.route("/chat")
def get_bot_response():    
    user_query = request.args.get('msg')
    cb = cb_obj.get("cb")
    if cb is None:
        # Handle case where cb is not initialized
        return "Chat backend not initialized", 500
       
    data = cb.get_data(user_query)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=False)