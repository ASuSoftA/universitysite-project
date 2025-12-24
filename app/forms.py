from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email

class LibraryFileForm(FlaskForm):

    title = StringField(
        'عنوان الملف',
        validators=[Optional()]
        #validators=[
           # DataRequired(message='عنوان الملف مطلوب'),
            #Length(max=200)
        #]
    )

    # ✅ الوصف اختياري
    description = TextAreaField(
        'الوصف',
        validators=[Optional()]
    )

    file_type = SelectField(
        'نوع الملف',
        choices=[
            ('book', 'كتاب'),
            ('handout', 'ملزمة'),
            ('exam', 'امتحان'),
            ('notes', 'ملاحظات'),
            ('other', 'أخرى')
        ],
        validators=[DataRequired(message='نوع الملف مطلوب')]
    )

    # ✅ أصبح إجباري
    course = StringField(
        'المادة',
        validators=[
            DataRequired(message='المادة مطلوبة'),
            Length(max=100)
        ]
    )

    # ✅ أصبح إجباري
    semester = SelectField(
        'الفصل الدراسي',
        choices=[
            ('', 'اختر الفصل'),
            ('first', 'الفصل الأول'),
            ('second', 'الفصل الثاني')
        ],
        validators=[DataRequired(message='الفصل الدراسي مطلوب')]
    )

    # ✅ أصبح إجباري (يعمل مع hidden input)
    faculty = SelectField(
        'الكلية',
        coerce=int,
        validators=[DataRequired(message='الكلية مطلوبة')]
    )

    # ✅ إجباري تلقائيًا
    file = FileField(
        'الملف',
        validators=[
            FileRequired(message='يجب اختيار ملف'),
            FileAllowed(
                ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar'],
                'يسمح فقط بملفات: PDF, Word, PowerPoint, Excel, ZIP, RAR'
            )
        ]
    )

    is_published = BooleanField('نشر فوري', default=True)
    submit = SubmitField('رفع الملف')

class SuggestionForm(FlaskForm):
    type = SelectField(
        'النوع',
        choices=[('suggestion', 'اقتراح'), ('complaint', 'شكوى')],
        validators=[DataRequired()]
    )
    title = StringField(
        'العنوان',
        validators=[DataRequired(), Length(max=200)]
    )
    content = TextAreaField(
        'المحتوى',
        validators=[DataRequired()]
    )
    faculty_id = SelectField(
        'اختر الكلية',
        coerce=int,  # يحول القيمة القادمة من select إلى عدد صحيح
        validators=[DataRequired()]
    )
    submit = SubmitField('إرسال')
    #sender_name = StringField('اسمك', validators=[DataRequired()])
    #sender_email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])


class PostForm(FlaskForm):
    title = StringField('عنوان المنشور',
                        validators=[Optional(), Length(max=200)])
    content = TextAreaField('المحتوى', validators=[Optional()])
    post_type = SelectField('نوع المنشور',
                            choices=[('text', 'نص'), ('image', 'صورة'),
                                     ('video', 'فيديو')],
                            default='text')
    images = FileField('صور المنشور',
                       render_kw={'multiple': True},
                       validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    video = FileField('فيديو',
                      validators=[
                          FileAllowed(['mp4', 'mov', 'avi'],
                                      'يسمح فقط بفيديو mp4, mov, avi')
                      ])
    
    is_published = BooleanField('نشر فوري', default=True)
    submit = SubmitField('نشر')


