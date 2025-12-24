# main_routes.py
from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models.post import Post, Like
from app.models.user import User
from flask_login import login_required, current_user
from app.models.faculty import Faculty  # ✅ هذا ضروري

#main_bp = Blueprint('main', __name__)

main_bp = Blueprint('main', __name__, template_folder='templates/main')

# -----------------------------
# Like Post
# -----------------------------
@main_bp.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)

        if current_user.is_authenticated:
            user_id = current_user.id
            existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        else:
            user_ip = request.remote_addr
            existing_like = Like.query.filter_by(post_id=post_id, user_ip=user_ip).first()

        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify({
                'liked': False,
                'likes_count': post.likes.count(),
                'message': 'تم إزالة الإعجاب'
            })
        else:
            new_like = Like(post_id=post_id)
            if current_user.is_authenticated:
                new_like.user_id = current_user.id
            else:
                new_like.user_ip = request.remote_addr
            db.session.add(new_like)
            db.session.commit()
            return jsonify({
                'liked': True,
                'likes_count': post.likes.count(),
                'message': 'تم إضافة الإعجاب'
            })

    except Exception as e:
        print(f"❌ خطأ في الإعجاب: {e}")
        return jsonify({'error': 'حدث خطأ'}), 500


# -----------------------------
# Share Post
# -----------------------------
@main_bp.route('/share/<int:post_id>', methods=['POST'])
def share_post(post_id):
    try:
        print(f"📤 طلب مشاركة للمنشور {post_id}")
        # يمكنك إضافة منطق المشاركة هنا لاحقاً
        return jsonify({
            'shared': True,
            'message': 'تم المشاركة بنجاح'
        })
        
    except Exception as e:
        print(f"❌ خطأ في المشاركة: {e}")
        return jsonify({'error': 'حدث خطأ'}), 500


# -----------------------------
# الصفحة الرئيسية - كل المنشورات المنشورة + إحصائيات
# -----------------------------
@main_bp.route('/home')
def index():
    try:
        posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()

        # إحصائيات
        stats = {
            'total_posts': Post.query.count() or 0,
            'total_users': User.query.count() or 0,
            'published_posts': len(posts),
            'total_likes': Like.query.count() or 0
        }

        return render_template('main/index.html', posts=posts, stats=stats)

    except Exception as e:
        print(f"❌ خطأ في index route: {e}")
        import traceback
        traceback.print_exc()
        return render_template('main/index.html',
                               posts=[],
                               stats={
                                   'total_posts': 0,
                                   'total_users': 0,
                                   'published_posts': 0,
                                   'total_likes': 0
                               })


# -----------------------------
# صفحة كلية محددة
# -----------------------------
@main_bp.route('/faculty/<faculty_name>')
def faculty_posts(faculty_name):
    page = request.args.get('page', 1, type=int)

    # احصل على كائن الكلية
    faculty_obj = Faculty.query.filter_by(name=faculty_name).first_or_404()

    # احصل على المنشورات الخاصة بهذه الكلية
    posts = Post.query.filter(
        Post.faculty == faculty_obj,
        Post.is_published == True
    ).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=12)

    # مرر الكائن للقالب
    return render_template(
        'main/faculty.html',
        posts=posts,
        faculty=faculty_obj  # ⚡ الآن القالب يحصل على الكائن كامل
    )


# -----------------------------
# Splash Screen
# -----------------------------
@main_bp.route('/')
def splash():
    return render_template('main/splashscreen.html')
