
from flask import Flask, render_template, request
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

index_filename = 'chat.html'

@app.route("/")
def home():    
    return render_template(index_filename)

@app.route("/chat")
def get_bot_response():    
    user_query = request.args.get('msg')    
    data = cb.get_data(user_query)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=False)