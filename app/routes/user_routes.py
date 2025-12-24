from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.post import Post
from config import Config
from datetime import datetime
from app.models.post import Post, Like  # ✅ الاستيراد الصحيح
# ✅ استورد الدالة من admin_routes
#from app.routes.admin_routes import save_uploaded_file
# استورد من utils
from app.utils.helpers import save_uploaded_file, allowed_file

user_bp = Blueprint('user_control', __name__)

# في app/routes/user_routes.py، أضف هذه الدالة قبل الـ routes
def save_uploaded_file(file, folder, allowed_extensions):
    if file and file.filename:
        original_filename = secure_filename(file.filename)
        name, ext = os.path.splitext(original_filename)
        
        if not ext:
            content_type = file.content_type.lower()
            if 'image' in content_type:
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.png'
            elif 'video' in content_type:
                ext = '.mp4'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{name}{ext}"
        file_path = os.path.join(folder, unique_filename)
        
        os.makedirs(folder, exist_ok=True)
        file.save(file_path)
        return unique_filename
    
    return None

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
           

@user_bp.route('/user/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_control.dashboard'))
    # إحصائيات المستخدم
    user_stats = {
        'my_posts': Post.query.filter_by(user_id=current_user.id).count(),
        'my_likes': 0,  # يمكن إضافة حساب الإعجابات لاحقاً
        'my_views': 0
    }

    # آخر 5 منشورات
    my_posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()).limit(5).all()

    return render_template('user/dashboard.html',
                           user_stats=user_stats,
                           my_posts=my_posts)


@user_bp.route('/user/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # معالجة صورة البروفايل فقط
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']
            if profile_image.filename != '':
                # حذف الصورة القديمة إذا لم تكن افتراضية
                if current_user.profile_image and current_user.profile_image != 'default_profile.png':
                    old_image_path = os.path.join(Config.UPLOAD_FOLDER,
                                                  'images',
                                                  current_user.profile_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # حفظ الصورة الجديدة
                image_filename = save_uploaded_file(
                    profile_image, os.path.join(Config.UPLOAD_FOLDER,
                                                'images'),
                    Config.ALLOWED_IMAGE_EXTENSIONS)
                if image_filename:
                    current_user.profile_image = image_filename
                    db.session.commit()
                    flash('تم تحديث صورة البروفايل بنجاح!')
                    
                if request.args.get('from_admin'):
                    return redirect(url_for('admin_control.edit_profile'))
                else:
                    return redirect(url_for('user_control.edit_profile'))

    return render_template('user/edit_profile.html')


@user_bp.route('/user/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # التحقق من كلمة المرور الحالية
        if not current_user.check_password(current_password):
            flash('كلمة المرور الحالية غير صحيحة')
            return render_template('user/change_password.html')

        # التحقق من تطابق كلمات المرور الجديدة
        if new_password != confirm_password:
            flash('كلمات المرور الجديدة غير متطابقة')
            return render_template('user/change_password.html')

        # تغيير كلمة المرور
        current_user.set_password(new_password)
        db.session.commit()

        flash('تم تغيير كلمة المرور بنجاح!')
        if request.args.get('from_admin'):
            return redirect(url_for('admin_control.dashboard'))
        else:
            return redirect(url_for('user_control.dashboard'))

    return render_template('user/change_password.html')


@user_bp.route('/user/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    # التحقق من صلاحية إضافة المنشورات
    if not current_user.can_create_posts():
        flash('ليس لديك صلاحية لإضافة المنشورات')
        return redirect(url_for('user_control.dashboard'))
    
    if request.method == 'POST':
        # جميع الحقول اختيارية
        title = request.form.get('title', '').strip() or None
        content = request.form.get('content', '').strip() or None
        post_type = 'text'  # افتراضي نص، سيتم التحديث إذا كان هناك صورة أو فيديو
        
        # التحقق من أن هناك محتوى على الأقل
        has_image = 'image' in request.files and request.files['image'].filename != ''
        has_video = 'video' in request.files and request.files['video'].filename != ''
        
        if not title and not content and not has_image and not has_video:
            flash('يجب إضافة محتوى على الأقل (عنوان، نص، صورة، أو فيديو)')
            return render_template('user/new_post.html')
        
        # -----------------------------
        # تحديد الكلية (استخدام العلاقة مباشرة)
        # -----------------------------
        faculty_obj = current_user.faculty  # كائن Faculty المرتبط بالمستخدم
        if not faculty_obj:
            flash('الكلية الخاصة بك غير معرفة، يرجى التواصل مع الإدارة')
            return redirect(url_for('user_control.dashboard'))
        
        # -----------------------------
        # إنشاء المنشور الجديد
        # -----------------------------
        new_post = Post(
            title=title,
            content=content,
            post_type=post_type,
            is_published=True,
            user_id=current_user.id,
            faculty=faculty_obj  # ربط المنشور مباشرة بالكلية
        )
        
        # معالجة تحميل الصور
        if has_image:
            image = request.files['image']
            if allowed_file(image.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
                image_filename = save_uploaded_file(
                    image, 
                    os.path.join(Config.UPLOAD_FOLDER, 'images'),
                    Config.ALLOWED_IMAGE_EXTENSIONS
                )
                if image_filename:
                    new_post.image_path = image_filename
                    new_post.post_type = 'image'
            else:
                flash('نوع الصورة غير مدعوم. يرجى رفع صورة بصيغة PNG, JPG, أو GIF')
        
        # معالجة تحميل الفيديوهات
        if has_video:
            video = request.files['video']
            if allowed_file(video.filename, Config.ALLOWED_VIDEO_EXTENSIONS):
                video_filename = save_uploaded_file(
                    video,
                    os.path.join(Config.UPLOAD_FOLDER, 'videos'),
                    Config.ALLOWED_VIDEO_EXTENSIONS
                )
                if video_filename:
                    new_post.video_path = video_filename
                    new_post.post_type = 'video'
            else:
                flash('نوع الفيديو غير مدعوم. يرجى رفع فيديو بصيغة MP4, MOV, أو AVI')
        
        # -----------------------------
        # حفظ المنشور في قاعدة البيانات
        # -----------------------------
        db.session.add(new_post)
        db.session.commit()
        
        flash('تم إضافة المنشور بنجاح!')
        return redirect(url_for('user_control.dashboard'))
    
    return render_template('user/new_post.html')

