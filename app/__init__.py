from flask import Flask, render_template
from flask_admin import Admin
from app.extensions import db, login_manager
from flask import redirect, url_for

# تهيئة لوحة التحكم
admin = Admin(name='لوحة التحكم', template_mode='bootstrap4')

def create_app():
    
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SECRET_KEY'] = '123'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_control.login'
    login_manager.login_message = 'يجب تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'warning'
    admin.init_app(app)

    # ✅ استيراد جميع النماذج قبل db.create_all()
    with app.app_context():
        from app.models.user import User
        #from app.models.post import Post, Like
        #from app.models.post import PostImage  # تأكد أن PostImage مستورد هنا
        from app.models.post import Post, PostImage, Like
        from app.models.faculty import Faculty
        from app.models.library import LibraryFile

        db.create_all()

        # ✅ إنشاء مستخدم admin افتراضي
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin', 
                is_admin=True,
                is_super_admin=True,   # ← مدير مطلق
                is_active=True,
                can_post=True,
                can_upload_books=True,
                profile_image='default_profile.png',
                faculty=None)
            admin_user.set_password('admin199')
             
            db.session.add(admin_user)
            db.session.commit()
            print("✅ تم إنشاء المستخدم الافتراضي: admin / admin199")


    # ✅ تسجيل الـ Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.user_routes import user_bp
    from app.routes.chat_routes import chat_bp
    from app.routes.knowledge_routes import knowledge_bp
    from app.routes.suggestions_routes import suggestions_bp
    from app.routes.library_routes import library_bp
    from app.routes.splash_routes import splash_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(chat_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(suggestions_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(splash_bp)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/chat')
    def chat_page():
        return render_template('chatbot.html')
    
    return app
