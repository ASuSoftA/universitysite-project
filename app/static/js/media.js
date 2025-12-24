// app/static/js/media.js
console.log('🎯 تحميل نظام الوسائط...');

function enhanceMediaDisplay() {
    console.log('🖼️ تحسين عرض الوسائط...');
    
    // تحسين الصور
    const images = document.querySelectorAll('.media-container img');
    images.forEach(img => {
        // إضافة loading lazy
        img.loading = 'lazy';
        
        // تحسين العرض عند الخطأ
        img.onerror = function() {
            this.style.display = 'none';
            console.log('❌无法加载图片:', this.src);
        };
        
        // تأثير عند التحميل
        img.onload = function() {
            this.style.opacity = '1';
            console.log('✅ تم تحميل الصورة:', this.src);
        };
    });
    
    // تحسين الفيديوهات
    const videos = document.querySelectorAll('video');
    videos.forEach(video => {
        // إعدادات الفيديو
        video.preload = 'metadata';
        video.playsInline = true;
        
        // إضافة عناصر تحكم مثل الفيسبوك
        video.addEventListener('loadedmetadata', function() {
            console.log('🎥 معلومات الفيديو:', this.videoWidth, 'x', this.videoHeight);
        });
    });
    
    // إضافة تأثيرات التفاعل
    const mediaContainers = document.querySelectorAll('.media-wrapper');
    mediaContainers.forEach(container => {
        container.addEventListener('click', function(e) {
            if (e.target.tagName !== 'VIDEO' && e.target.tagName !== 'BUTTON') {
                const video = this.querySelector('video');
                if (video) {
                    video.paused ? video.play() : video.pause();
                }
            }
        });
    });
}

// بدء التشغيل
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceMediaDisplay);
} else {
    enhanceMediaDisplay();
}