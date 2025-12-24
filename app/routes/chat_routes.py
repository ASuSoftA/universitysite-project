from flask import Blueprint, request, jsonify, current_app
from app.ai_model.chatbot import UniversityChatbot

chat_bp = Blueprint('chat', __name__)
chatbot = UniversityChatbot()

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        # التحقق من وجود JSON
        if not request.is_json:
            return jsonify({'error': 'الطلب يجب أن يكون بصيغة JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'لا يوجد بيانات'}), 400
        
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        
        # جرب رداً بسيطاً أولاً للاختبار
        response = chatbot.generate_response(user_message)
        return jsonify({'response': response})
    
    except Exception as e:
        current_app.logger.error(f"Error in chat route: {str(e)}")
        return jsonify({'error': f'حدث خطأ في الخادم: {str(e)}'}), 500
    
