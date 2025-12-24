from flask import Blueprint, render_template, url_for

# إنشاء Blueprint خاص بالشاشة الترحيبية
splash_bp = Blueprint('splash_bp', __name__, template_folder='../templates/main')

@splash_bp.route('/splash')
def splash():
    """
    Route لعرض شاشة الترحيب.
    بعد 5 ثوانٍ، يتم إعادة التوجيه تلقائيًا للصفحة الرئيسية.
    """
    # render_template يعرض HTML الشاشة الترحيبية
    return render_template('splashscreen.html')
