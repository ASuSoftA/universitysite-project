from flask import Blueprint, render_template, request, jsonify
from app.ai_model.university_knowledge import university_data

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/admin/knowledge')
def manage_knowledge():
    """عرض واجهة إدارة المحتوى"""
    return render_template('admin/knowledge_management.html', data=university_data)

@knowledge_bp.route('/api/update_knowledge', methods=['POST'])
def update_knowledge():
    """تحديث المحتوى (للمسؤولين فقط)"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        subtopic = data.get('subtopic')
        content = data.get('content')
        
        # هنا يمكنك إضافة التحقق من الصلاحيات
        
        if subtopic:
            university_data[topic][subtopic] = content
        else:
            university_data[topic] = content
            
        return jsonify({'success': True, 'message': 'تم تحديث المحتوى بنجاح'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})