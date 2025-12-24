# find_template_errors.py
with open('app/templates/main/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
lines = content.split('\n')
block_count = 0
endblock_count = 0

print("🔍 البحث عن أخطاء القالب:")
for i, line in enumerate(lines, 1):
    if '{% block ' in line:
        block_count += 1
        print(f"📦 السطر {i}: {line.strip()}")
    elif '{% endblock %}' in line:
        endblock_count += 1
        print(f"🔚 السطر {i}: {line.strip()}")

print(f"\n📊 الإحصائية: {block_count} block, {endblock_count} endblock")
if block_count != endblock_count:
    print("❌ خطأ: عدد blocks لا يساوي number of endblocks!")
else:
    print("✅ الهيكل صحيح")