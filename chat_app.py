
from flask import Flask, render_template, request, redirect, url_for
from flask_caching import Cache

from chat_backend import ChatBackend
import atexit
from flask import jsonify

app = Flask(__name__)

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 0
}
app.config.from_mapping(config)
cache = Cache(app)

cb = ChatBackend(cache)

#cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Function to delete the object
def cleanup():
    global cb
    global cache

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
    data = cb.get_session_names()
    return jsonify(data)

@app.route("/set_session")
def set_session():
    session_name = request.args.get('session')  
    print("Session Name:", session_name)  
    cb.set_session(session_name)
    #return redirect(url_for('chat'))
    return "/chat.html"

@app.route("/chat")
def get_bot_response():    
    user_query = request.args.get('msg')    
    data = cb.get_data(user_query)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=False)