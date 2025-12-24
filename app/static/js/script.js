// app/static/js/script.js
console.log('✅ تم تحميل script.js بنجاح');

// دالة بسيطة للتحقق
function checkScriptLoaded() {
    console.log('🎯 script.js يعمل بشكل صحيح');
    return true;
}

// يمكنك إضافة دوال أخرى هنا لاحقاً
checkScriptLoaded();

btn.classList.toggle("active-like");
btn.classList.add("burst");
setTimeout(() => btn.classList.remove("burst"), 400);
