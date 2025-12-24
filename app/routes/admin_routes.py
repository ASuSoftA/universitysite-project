import os
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect, url_for, flash, current_app)
from flask_login import (login_required, current_user, login_user, logout_user)
from werkzeug.utils import secure_filename
from app import db, login_manager
from app.models.user import User
from app.models.post import Post, Like
from config import Config
import uuid
from flask import session
from flask import jsonify
from app.models.faculty import Faculty
from flask import abort
from app.utils.upload import save_image


admin_bp = Blueprint('admin_control', __name__, url_prefix='/admin')

# ==========================
# Helpers
# ==========================

def save_uploaded_file(file, folder, allowed_extensions):
    """
    حفظ ملف مرفوع (صورة أو فيديو) في المجلد المحدد مع التحقق من الامتداد
    Args:
        file: ملف مرفوع من request.files
        folder: مجلد الوجهة للحفظ
        allowed_extensions: قائمة الامتدادات المسموح بها (مثلاً ['jpg','png','mp4'])
    Returns:
        اسم الملف المحفوظ (str) أو None إذا لم يتم الحفظ
    """
    if file and file.filename:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()

        # التحقق من أن الامتداد مسموح
        if ext not in allowed_extensions:
            current_app.logger.warning(f"⚠️ امتداد غير مسموح: {ext}")
            return None

        # إنشاء اسم فريد للملف لتجنب التكرار
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.{ext}"
        
        # إنشاء المجلد إذا لم يكن موجود
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, unique_filename)
        
        # حفظ الملف
        file.save(file_path)
        current_app.logger.info(f"✅ File saved: {file_path}")
        return unique_filename

    return None


# ==========================
# User Management
# ==========================

@admin_bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('admin_control.login'))

    # المدير المطلق يرى الجميع
    if current_user.is_super_admin:
        users = User.query.order_by(User.created_at.desc()).all()

    # مدير كلية يرى مستخدمي كليته فقط
    else:
        if not current_user.faculty_id:
            flash('لم يتم تحديد الكلية لهذا الحساب')
            return redirect(url_for('admin_control.dashboard'))

        users = User.query.filter_by(
            faculty_id=current_user.faculty_id
        ).order_by(User.created_at.desc()).all()

    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    # =========================
    # GET
    # =========================
    if request.method == 'GET':
        if current_user.is_super_admin:
            faculties = Faculty.query.order_by(Faculty.name).all()
            return render_template(
                'admin/new_user.html',
                faculties=faculties,
                faculty=None
            )
        else:
            if not current_user.faculty_id:
                flash('لم يتم تحديد الكلية لهذا المدير')
                return redirect(url_for('admin_control.dashboard'))

            faculty = Faculty.query.get_or_404(current_user.faculty_id)
            return render_template(
                'admin/new_user.html',
                faculty=faculty
            )

    # =========================
    # POST
    # =========================
    username = request.form['username'].strip()
    password = request.form['password']

    # تحديد الكلية
    if current_user.is_super_admin:
        faculty_id = request.form.get('faculty_id')
        if not faculty_id:
            flash('يرجى اختيار الكلية')
            return redirect(url_for('admin_control.new_user'))

        faculty = Faculty.query.get_or_404(faculty_id)
    else:
        faculty = Faculty.query.get_or_404(current_user.faculty_id)

    # منع تكرار المستخدم داخل نفس الكلية
    if User.query.filter_by(username=username, faculty_id=faculty.id).first():
        flash('اسم المستخدم موجود بالفعل في هذه الكلية')
        return redirect(url_for('admin_control.new_user'))

    new_user = User(
        username=username,
        faculty_id=faculty.id,
        is_admin='is_admin' in request.form and current_user.is_super_admin,
        is_super_admin=False,
        can_post='can_post' in request.form,
        can_upload_books='can_upload_books' in request.form,
        is_active=True
    )
    new_user.set_password(password)

    # صورة البروفايل
    if 'profile_image' in request.files:
        image = request.files['profile_image']
        if image and image.filename:
            filename = save_uploaded_file(
                image,
                os.path.join(Config.UPLOAD_FOLDER, 'images'),
                Config.ALLOWED_IMAGE_EXTENSIONS
            )
            if filename:
                new_user.profile_image = filename

    db.session.add(new_user)
    db.session.commit()

    flash('تم إضافة المستخدم بنجاح')
    return redirect(url_for('admin_control.manage_users'))

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    if not current_user.is_super_admin:
        if user.faculty_id != current_user.faculty_id:
            flash('غير مسموح لك بتعديل مستخدم من كلية أخرى')
            return redirect(url_for('admin_control.manage_users'))

        if user.is_admin:
            flash('لا يمكنك تعديل مستخدم بصلاحية مدير')
            return redirect(url_for('admin_control.manage_users'))

    if request.method == 'POST':
        user.username = request.form.get('username').strip()

        if current_user.is_super_admin:
            new_password = request.form.get('new_password')
            if new_password:
                if len(new_password) < 6:
                    flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
                    return redirect(url_for('admin_control.edit_user', user_id=user.id))
                user.set_password(new_password)

            user.is_admin = 'is_admin' in request.form

        user.can_post = 'can_post' in request.form
        user.can_upload_books = 'can_upload_books' in request.form

        db.session.commit()
        flash('تم تحديث بيانات المستخدم بنجاح!')
        return redirect(url_for('admin_control.manage_users'))

    return render_template('admin/edit_user.html', user=user)
@admin_bp.route('/users/toggle_active/<int:user_id>')
@login_required
def toggle_user_active(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    if user_id == current_user.id:
        flash('لا يمكنك تعطيل حسابك الخاص!')
        return redirect(url_for('admin_control.manage_users'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    status = "تفعيل" if user.is_active else "تعطيل"
    flash(f'تم {status} المستخدم بنجاح!')
    return redirect(url_for('admin_control.manage_users'))
@admin_bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    if user_id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص!')
        return redirect(url_for('admin_control.manage_users'))

    user = User.query.get_or_404(user_id)

    if not current_user.is_super_admin:
        if user.faculty_id != current_user.faculty_id or user.is_admin:
            flash('غير مسموح لك بحذف هذا المستخدم')
            return redirect(url_for('admin_control.manage_users'))

    if user.profile_image and user.profile_image != 'default_profile.png':
        profile_path = os.path.join(Config.UPLOAD_FOLDER, 'images', user.profile_image)
        if os.path.exists(profile_path):
            os.remove(profile_path)

    db.session.delete(user)
    db.session.commit()

    flash('تم حذف المستخدم بنجاح!')
    return redirect(url_for('admin_control.manage_users'))

@admin_bp.route('/select-faculty', methods=['GET', 'POST'])
@login_required
def select_faculty():
    if not current_user.is_super_admin:
        flash('غير مصرح لك')
        return redirect(url_for('admin_control.dashboard'))

    # جلب الكليات من قاعدة البيانات مباشرة
    faculties = Faculty.query.order_by(Faculty.name).all()

    if request.method == 'POST':
        selected_faculty_id = request.form.get('faculty_id')

        if not selected_faculty_id:
            flash('يرجى اختيار الكلية')
            return redirect(url_for('admin_control.select_faculty'))

        faculty_obj = Faculty.query.get(selected_faculty_id)
        if not faculty_obj:
            flash('الكلية غير موجودة!')
            return redirect(url_for('admin_control.select_faculty'))

        # حفظ الـ ID في الجلسة
        session['current_faculty_id'] = faculty_obj.id

        flash(f'تم الدخول إلى كلية {faculty_obj.name}')
        return redirect(url_for('admin_control.dashboard'))

    return render_template(
        'admin/select_faculty.html',
        faculties=faculties
    )

# ==========================
# Post Management
# ==========================

@admin_bp.route('/posts')
@login_required
def manage_posts():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية')
        return redirect(url_for('auth.login'))

    # المدير المطلق يرى جميع المنشورات
    if current_user.is_super_admin:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    # مدير الكلية يرى كل منشورات كليته
    else:
        posts = Post.query.filter(
            Post.faculty == current_user.faculty
        ).order_by(Post.created_at.desc()).all()

    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    # -----------------------------
    # التحقق من الصلاحيات
    # -----------------------------
    if not (current_user.is_admin or current_user.can_post):
        flash('ليس لديك صلاحية إضافة منشور')
        return redirect(url_for('main.index'))

    # -----------------------------
    # POST
    # -----------------------------
    if request.method == 'POST':
        title = request.form.get('title', '').strip() or None
        content = request.form.get('content', '').strip() or None
        post_type = request.form.get('post_type', 'text')
        is_published = 'is_published' in request.form

        # -----------------------------
        # تحديد الكلية بشكل صحيح
        # -----------------------------
        faculty_obj = None

        if current_user.is_super_admin:
            faculty_id = request.form.get('faculty_id')

            if not faculty_id:
                flash('يرجى اختيار الكلية')
                return redirect(url_for('admin_control.new_post'))

            faculty_obj = Faculty.query.get(faculty_id)

        else:
            if not current_user.faculty:
                flash('لم يتم تحديد كلية لهذا الحساب')
                return redirect(url_for('admin_control.dashboard'))

            #faculty_obj = Faculty.query.filter_by(name=current_user.faculty).first()
            faculty_obj = Faculty.query.get(current_user.faculty_id)

        if not faculty_obj:
            flash('الكلية المحددة غير موجودة')
            return redirect(url_for('admin_control.new_post'))

        # -----------------------------
        # إنشاء المنشور
        # -----------------------------
        post = Post(
            title=title,
            content=content,
            post_type=post_type,
            is_published=is_published,
            faculty=faculty_obj,   # كائن Faculty
            user_id=current_user.id
        )

        # -----------------------------
        # رفع صورة
        # -----------------------------
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                filename = save_uploaded_file(
                    image,
                    os.path.join(
                        current_app.root_path,
                        'static', 'uploads', 'images'
                    ),
                    Config.ALLOWED_IMAGE_EXTENSIONS
                )
                if filename:
                    post.image_path = filename
                    post.post_type = 'image'

        # -----------------------------
        # رفع فيديو
        # -----------------------------
        if 'video' in request.files:
            video = request.files['video']
            if video and video.filename:
                video_filename = save_uploaded_file(
                    video,
                    os.path.join(
                        current_app.root_path,
                        'static', 'uploads', 'videos'
                    ),
                    Config.ALLOWED_VIDEO_EXTENSIONS
                )
                if video_filename:
                    post.video_path = video_filename
                    post.post_type = 'video'

        # -----------------------------
        # التحقق من وجود محتوى
        # -----------------------------
        if not title and not content and not post.image_path and not post.video_path:
            flash('يجب إضافة محتوى واحد على الأقل (عنوان، نص، صورة، أو فيديو)')
            return redirect(url_for('admin_control.new_post'))

        # -----------------------------
        # الحفظ
        # -----------------------------
        db.session.add(post)
        db.session.commit()

        flash('تم إضافة المنشور بنجاح')
        return redirect(url_for('admin_control.manage_posts'))

    # -----------------------------
    # GET
    # -----------------------------
    faculties = Faculty.query.all()
    return render_template(
        'admin/new_post.html',
        faculties=faculties
    )

@admin_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    post = Post.query.get_or_404(post_id)

    # 🔒 منع مدير الكلية من تعديل منشورات كلية أخرى
    if not current_user.is_super_admin:
        if post.faculty != current_user.faculty:
            flash('غير مسموح لك بالوصول إلى هذا المنشور')
            return redirect(url_for('admin_control.manage_posts'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip() or None
        content = request.form.get('content', '').strip() or None
        post_type = request.form.get('post_type', 'text')
        is_published = 'is_published' in request.form

        post.title = title
        post.content = content
        post.post_type = post_type
        post.is_published = is_published
        post.updated_at = datetime.now()

        # تحديث الصورة
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                if post.image_path:
                    old_image_path = os.path.join(Config.UPLOAD_FOLDER, 'images', post.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                image_filename = save_uploaded_file(
                    image,
                    os.path.join(Config.UPLOAD_FOLDER, 'images'),
                    Config.ALLOWED_IMAGE_EXTENSIONS
                )
                if image_filename:
                    post.image_path = image_filename
                    post.post_type = 'image'

        # تحديث الفيديو
        if 'video' in request.files:
            video = request.files['video']
            if video and video.filename:
                if post.video_path:
                    old_video_path = os.path.join(Config.UPLOAD_FOLDER, 'videos', post.video_path)
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)

                video_filename = save_uploaded_file(
                    video,
                    os.path.join(Config.UPLOAD_FOLDER, 'videos'),
                    Config.ALLOWED_VIDEO_EXTENSIONS
                )
                if video_filename:
                    post.video_path = video_filename
                    post.post_type = 'video'

        db.session.commit()
        flash('تم تحديث المنشور بنجاح!')
        return redirect(url_for('admin_control.manage_posts'))

    return render_template('admin/edit_post.html', post=post)

@admin_bp.route('/posts/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    post = Post.query.get_or_404(post_id)

    # 🔒 منع مدير الكلية من حذف منشورات كلية أخرى
    if not current_user.is_super_admin:
        if post.faculty != current_user.faculty:
            flash('غير مسموح لك بحذف هذا المنشور')
            return redirect(url_for('admin_control.manage_posts'))

    # حذف الملفات المرتبطة
    if post.image_path:
        image_path = os.path.join(Config.UPLOAD_FOLDER, 'images', post.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

    if post.video_path:
        video_path = os.path.join(Config.UPLOAD_FOLDER, 'videos', post.video_path)
        if os.path.exists(video_path):
            os.remove(video_path)

    db.session.delete(post)
    db.session.commit()

    flash('تم حذف المنشور بنجاح!')
    return redirect(url_for('admin_control.manage_posts'))

@admin_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('admin/view_post.html', post=post)

# -----------------------------
# تبديل حالة النشر للمنشور
# -----------------------------

@admin_bp.route('/posts/toggle_publish/<int:post_id>')
@login_required
def toggle_publish(post_id):
    try:
        post = Post.query.get_or_404(post_id)

        # التأكد من صلاحية الوصول
        if not (current_user.is_super_admin or post.faculty == current_user.faculty):
            flash('ليس لديك صلاحية لتعديل هذا المنشور', 'danger')
            return redirect(url_for('admin_control.manage_posts'))

        # تبديل حالة النشر
        post.is_published = not post.is_published
        db.session.commit()

        flash(f"تم {'نشر' if post.is_published else 'إخفاء'} المنشور بنجاح!", 'success')
        return redirect(url_for('admin_control.manage_posts'))

    except Exception as e:
        print(f"❌ خطأ في toggle_publish: {e}")
        flash('حدث خطأ أثناء تغيير حالة النشر', 'danger')
        return redirect(url_for('admin_control.manage_posts'))

# ==========================
# Authentication
# ==========================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_control.dashboard'))

    faculties = Faculty.query.order_by(Faculty.name).all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        faculty_id = request.form.get('faculty_id')

        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور')
            return render_template('admin/login.html', faculties=faculties)

        # =========================
        # المدير المطلق (بدون كلية)
        # =========================
        user = User.query.filter_by(
            username=username,
            is_super_admin=True
        ).first()

        # =========================
        # مدير كلية / مستخدم عادي
        # =========================
        if not user:
            if not faculty_id:
                flash('يرجى اختيار الكلية')
                return render_template('admin/login.html', faculties=faculties)

            user = User.query.filter_by(
                username=username,
                faculty_id=faculty_id
            ).first()

        if not user or not user.check_password(password):
            flash('بيانات الدخول غير صحيحة')
            return render_template('admin/login.html', faculties=faculties)

        if not user.is_active:
            flash('الحساب معطل')
            return render_template('admin/login.html', faculties=faculties)

        login_user(user)

        # =========================
        # التوجيه
        # =========================
        if user.is_admin:
            return redirect(url_for('admin_control.dashboard'))

        return redirect(url_for('user_control.dashboard'))

    # GET
    return render_template('admin/login.html', faculties=faculties)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('current_faculty', None)  # مسح الكلية المختارة
    flash('تم تسجيل الخروج')
    return redirect(url_for('admin_control.login'))


# ==========================
# Dashboard
# ==========================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_super_admin:
        total_users = User.query.count()
        total_posts = Post.query.count()
    else:
        if not current_user.faculty_id:
            flash('لم يتم تحديد الكلية لهذا المدير')
            return redirect(url_for('admin_control.select_faculty'))

        total_users = User.query.filter_by(faculty_id=current_user.faculty_id).count()
        total_posts = Post.query.filter_by(faculty_id=current_user.faculty_id).count()

    # إرسال stats كـ dict
    stats = {
        'total_users': total_users,
        'total_posts': total_posts
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats  # ← هنا تم حل المشكلة
    )

# ==========================
# Knowledge Base Management
# ==========================

@admin_bp.route('/knowledge')
@login_required
def manage_knowledge():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    try:
        from app.ai_model.university_knowledge import university_data
        return render_template('admin/knowledge_management.html', data=university_data)
    except ImportError:
        flash('لم يتم العثور على قاعدة المعرفة', 'error')
        return redirect(url_for('admin_control.dashboard'))


@admin_bp.route('/faculty/settings', methods=['GET', 'POST'])
@login_required
def faculty_settings():
    if not current_user.is_admin:
        abort(403)

    if current_user.is_super_admin:
        faculty_id = request.args.get('faculty_id')
        if not faculty_id:
            abort(404)
        faculty = Faculty.query.get_or_404(faculty_id)
    else:
        faculty = current_user.faculty

    if request.method == 'POST':
        faculty.description = request.form.get('description')

        if 'cover_image' in request.files and request.files['cover_image'].filename:
            faculty.cover_image = save_image(request.files['cover_image'])

        if 'logo_image' in request.files and request.files['logo_image'].filename:
            faculty.logo_image = save_image(request.files['logo_image'])

        db.session.commit()
        flash('تم تحديث بيانات الكلية بنجاح', 'success')

    return render_template('admin/faculty_settings.html', faculty=faculty)
