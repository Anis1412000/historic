from flask import Flask, request, jsonify, render_template
from models import db, ChatHistory
from datetime import datetime
from sqlalchemy import or_, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/chatbot_history'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db.init_app(app)

# Routes principales
@app.route('/')
def home():
    return render_template('history.html')

# API Endpoints
@app.route('/api/save', methods=['POST'])
def save_entry():
    try:
        data = request.json
        entry = ChatHistory(
            user_prompt=data['prompt'],
            bot_response=data['response']
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({"status": "success", "id": entry.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        query = ChatHistory.query.order_by(desc(ChatHistory.timestamp))
        
        if search_term := request.args.get('q'):
            search_filter = or_(
                ChatHistory.user_prompt.ilike(f'%{search_term}%'),
                ChatHistory.bot_response.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        history = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            "entries": [entry.serialize() for entry in history.items],
            "total_pages": history.pages,
            "current_page": page
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    try:
        entry = ChatHistory.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)