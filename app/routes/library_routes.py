from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.extensions import db
from app.models.library import LibraryFile
from app.forms import LibraryFileForm
import os
import humanize
import string
import random
from datetime import datetime
from flask import current_app
from app.models.faculty import Faculty

library_bp = Blueprint('library', __name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_library_file(file: FileStorage, folder: str, allowed_extensions: set):
    """
    حفظ ملف في مجلد محدد مع التحقق من الامتداد وإضافة timestamp وراندوم string لمنع تكرار الأسماء.
    :param file: كائن FileStorage
    :param folder: مسار المجلد
    :param allowed_extensions: مجموعة الامتدادات المسموح بها
    :return: (اسم الملف المحفوظ, حجم الملف بالبايت) أو (None, 0) إذا فشل الحفظ
    """
    if not file or file.filename == '':
        return None, 0

    filename = file.filename
    name, ext = os.path.splitext(filename)
    ext = ext.lower().replace('.', '')

    if ext not in allowed_extensions:
        return None, 0

    # إنشاء اسم فريد للملف لتجنب التعارض
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{random_str}_{secure_filename(name)}.{ext}"

    # إنشاء المسار النهائي للملف
    file_path = os.path.join(folder, unique_filename)

    try:
        os.makedirs(folder, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجودًا
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        return unique_filename, file_size
    except Exception as e:
        current_app.logger.error(f"Error saving file '{filename}': {e}")
        return None, 0

@library_bp.route('/library')
def library():
    page = request.args.get('page', 1, type=int)
    file_type = request.args.get('type', 'all')
    course = request.args.get('course', '')
    semester = request.args.get('semester', '')
    faculty_filter = request.args.get('faculty', type=int)
    search_query = request.args.get('q', '').strip()

    query = LibraryFile.query.filter_by(is_published=True)

    if file_type != 'all':
        query = query.filter_by(file_type=file_type)

    if course:
        query = query.filter(LibraryFile.course.ilike(f'%{course}%'))

    if semester:
        query = query.filter_by(semester=semester)

    if faculty_filter:
        query = query.filter(LibraryFile.faculty_id == faculty_filter)
        
    if search_query:
     query = query.join(LibraryFile.faculty)  # join مع جدول الكليات
    query = query.filter(
        (LibraryFile.title.ilike(f'%{search_query}%')) |
        (LibraryFile.description.ilike(f'%{search_query}%')) |
        (LibraryFile.course.ilike(f'%{search_query}%')) |
        (LibraryFile.semester.ilike(f'%{search_query}%')) |
        (Faculty.name.ilike(f'%{search_query}%'))
    )

    faculties = Faculty.query.order_by(Faculty.name).all()

    files = query.order_by(LibraryFile.created_at.desc())\
             .paginate(page=1, per_page=10000)  # عدد كبير لعرض كل الملفات

    # المواد فقط من النتائج الحالية
    courses = db.session.query(LibraryFile.course)\
        .filter(LibraryFile.course.isnot(None))\
        .distinct()\
        .all()

    return render_template(
        'library/index.html',
        files=files,
        current_type=file_type,
        current_course=course,
        current_semester=semester,
        current_search=search_query,
        current_faculty=faculty_filter,
        faculties=faculties,
        courses=[c[0] for c in courses if c[0]]
    )


@library_bp.route('/library/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = LibraryFileForm()

    if not current_user.can_upload_to_library():
        flash('ليس لديك صلاحية لرفع الملفات', 'error')
        return redirect(url_for('library.library'))
    
    if request.method == 'POST':
         print(form.errors)

    form.faculty.choices = [
    (f.id, f.name) for f in Faculty.query.all()]

    if form.validate_on_submit():
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'library')
        file = form.file.data
        allowed_extensions = current_app.config.get('ALLOWED_LIBRARY_EXTENSIONS', set())
        max_size = current_app.config.get('MAX_FILE_SIZE', 50*1024*1024)

        if not file or not allowed_file(file.filename, allowed_extensions):
            flash(f'نوع الملف غير مدعوم. الصيغ المسموح بها: {", ".join(allowed_extensions)}', 'error')
            return render_template('library/upload.html', form=form)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > max_size:
            flash(f'حجم الملف كبير جدًا. الحد الأقصى: {max_size // (1024*1024)}MB', 'error')
            return render_template('library/upload.html', form=form)

        filename, saved_size = save_library_file(file, upload_folder, allowed_extensions)
        if not filename:
            flash('حدث خطأ أثناء رفع الملف', 'error')
            return render_template('library/upload.html', form=form)

        if current_user.is_super_admin:
           faculty_id = form.faculty.data
           if not faculty_id:
                flash('يرجى اختيار الكلية', 'error')
                return render_template('library/upload.html', form=form)
        else:
             faculty_id = current_user.faculty_id
 
        library_file = LibraryFile(
            title=form.title.data,
            description=form.description.data,
            filename=filename,
            file_type=form.file_type.data,
            course=form.course.data,
            semester=form.semester.data,
            uploader_id=current_user.id,
            faculty_id=faculty_id,
            file_size=saved_size,
            is_published=form.is_published.data
        )

        try:
            db.session.add(library_file)
            db.session.commit()
            flash('تم رفع الملف بنجاح!', 'success')
            # بعد الحفظ الناجح
            if current_user.is_admin:
               return redirect(url_for('library.admin_library'))
            else:
             return redirect(url_for('library.upload'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {e}")
            flash('حدث خطأ أثناء حفظ الملف في قاعدة البيانات', 'error')
            return render_template('library/upload.html', form=form)

    return render_template('library/upload.html', form=form)


@library_bp.route('/library/download/<int:file_id>')
def download_file(file_id):
    file = LibraryFile.query.get_or_404(file_id)
    
    if not file.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        flash('هذا الملف غير متاح للتحميل', 'error')
        return redirect(url_for('library.library'))

    # المسار الصحيح باستخدام current_app.root_path
    file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'library', file.filename)
    
    if not os.path.exists(file_path):
        flash('الملف غير موجود على الخادم', 'error')
        return redirect(url_for('library.library'))

    # زيادة عداد التحميلات
    file.download_count += 1
    db.session.commit()
    
    return send_file(file_path, as_attachment=True, download_name=file.title + os.path.splitext(file.filename)[1])


@library_bp.route('/library/file/<int:file_id>')
def file_details(file_id):
    file = LibraryFile.query.get_or_404(file_id)
    
    if not file.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        flash('هذا الملف غير متاح', 'error')
        return redirect(url_for('library.library'))
    
    return render_template('library/details.html', file=file, humanize=humanize)

# إدارة الملفات (للمسؤولين فقط)
@library_bp.route('/admin/library')
@login_required
def admin_library():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)

    # المدير المطلق يرى كل الملفات
    if current_user.is_super_admin:
        files_query = LibraryFile.query
    else:
        # مدير الكلية يرى كل الملفات التي تخص كليته
        files_query = LibraryFile.query.filter_by(faculty=current_user.faculty)
    
    files = files_query.order_by(LibraryFile.created_at.desc()).paginate(page=page, per_page=15)

    return render_template('admin/library.html', files=files)

@library_bp.route('/admin/library/toggle/<int:file_id>')
@login_required
def toggle_file_publish(file_id):
    file = LibraryFile.query.get_or_404(file_id)
    if not current_user.is_admin or (not current_user.is_super_admin and file.faculty_id != current_user.faculty_id
):
        flash('غير مسموح لك بالوصول إلى هذا الملف', 'error')
        return redirect(url_for('library.admin_library'))

    file.is_published = not file.is_published
    db.session.commit()
    flash(f"تم {'نشر' if file.is_published else 'إخفاء'} الملف بنجاح!", 'success')
    return redirect(url_for('library.admin_library'))


@library_bp.route('/admin/library/delete/<int:file_id>')
@login_required
def delete_file(file_id):
    file = LibraryFile.query.get_or_404(file_id)
    if not current_user.is_admin or (not current_user.is_super_admin and file.faculty_id != current_user.faculty_id
):
        flash('غير مسموح لك بحذف هذا الملف', 'error')
        return redirect(url_for('library.admin_library'))

    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'library', file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(file)
        db.session.commit()
        flash('تم حذف الملف بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting file: {e}")
        flash('حدث خطأ أثناء حذف الملف', 'error')

    return redirect(url_for('library.admin_library'))
