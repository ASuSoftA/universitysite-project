from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.suggestion import Suggestion
from app.forms import SuggestionForm
from app.models.faculty import Faculty

suggestions_bp = Blueprint('suggestions', __name__)

# واجهة الطلاب لإرسال الاقتراحات
@suggestions_bp.route('/suggestions/new', methods=['GET', 'POST'])
def new_suggestion():
    form = SuggestionForm()
    
    # جلب جميع الكليات لإظهارها في الـ select
    from app.models.faculty import Faculty
    faculties = Faculty.query.all()
    
    form.faculty_id.choices = [(f.id, f.name) for f in faculties]

    if form.validate_on_submit():
        try:
            faculty_id = request.form.get('faculty_id')
            suggestion = Suggestion(
                title=form.title.data,
                content=form.content.data,
                type=form.type.data,
                #sender_name=form.sender_name.data,
                #sender_email=form.sender_email.data,
                faculty_id=faculty_id,
                user_id=current_user.id if current_user.is_authenticated else None

            )
                     
            db.session.add(suggestion)
            db.session.commit()
            
            flash('تم إرسال {} بنجاح!'.format('اقتراحك' if form.type.data == 'suggestion' else 'شكواك'), 'success')
            return redirect(url_for('suggestions.new_suggestion'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء الإرسال: {e}', 'error')
    
    return render_template('suggestions/new.html', form=form, faculties=faculties)

# قائمة الاقتراحات الخاصة بالطالب
@suggestions_bp.route('/my-suggestions')
@login_required
def my_suggestions():
    page = request.args.get('page', 1, type=int)
    suggestions = Suggestion.query.filter_by(user_id=current_user.id)\
        .order_by(Suggestion.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('suggestions/my_suggestions.html', suggestions=suggestions)

@suggestions_bp.route('/admin/suggestions')
@login_required
def admin_suggestions():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', 'all')
    read_filter = request.args.get('read', 'all')  # ⭐ الجديد ⭐

    query = Suggestion.query

    # تقييد الاقتراحات حسب الكلية للمدير العادي
    if not getattr(current_user, 'is_super_admin', False):
        query = query.filter(Suggestion.faculty_id == current_user.faculty_id)

    # فلترة حسب النوع
    if type_filter != 'all':
        query = query.filter(Suggestion.type == type_filter)

    # ⭐ فلترة حسب المقروء / غير المقروء ⭐
    if read_filter == 'read':
        query = query.filter(Suggestion.is_read == True)
    elif read_filter == 'unread':
        query = query.filter(Suggestion.is_read == False)

    suggestions = query.order_by(
        Suggestion.created_at.desc()
    ).paginate(page=page, per_page=15)

    return render_template(
        'admin/suggestions.html',
        suggestions=suggestions,
        current_filter=type_filter,
        current_read_filter=read_filter  # ⭐ مهم للقالب ⭐
    )

# عرض اقتراح معين للإدارة
@suggestions_bp.route('/admin/suggestions/<int:suggestion_id>')
@login_required
def view_suggestion(suggestion_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))
    
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    
    # وضع علامة كمقروء
   # if not suggestion.is_read:
    #    suggestion.is_read = True
     #   db.session.commit()
    
    return render_template('admin/view_suggestion.html', suggestion=suggestion)

# حذف اقتراح (الإدارة فقط)
@suggestions_bp.route('/admin/suggestions/delete/<int:suggestion_id>')
@login_required
def delete_suggestion(suggestion_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة')
        return redirect(url_for('main.index'))
    
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    
    db.session.delete(suggestion)
    db.session.commit()
    
    flash('تم حذف {} بنجاح'.format('الاقتراح' if suggestion.type == 'suggestion' else 'الشكوى'), 'success')
    return redirect(url_for('suggestions.admin_suggestions'))

# API لوضع علامة كمقروء
@suggestions_bp.route('/admin/suggestions/mark-read/<int:suggestion_id>', methods=['POST'])
@login_required
def mark_as_read(suggestion_id):
    if not current_user.is_admin:
        flash('غير مصرح', 'error')
        return redirect(url_for('main.index'))

    suggestion = Suggestion.query.get_or_404(suggestion_id)
    suggestion.is_read = True
    db.session.commit()
    flash('تم وضع العلامة كمقروء', 'success')
    return redirect(url_for('suggestions.admin_suggestions'))
