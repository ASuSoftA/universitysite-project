// ====================== Start Interaction System ===========================
console.log("🚀 تشغيل نظام التفاعل...");

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// ==================== نظام الإعجاب ====================
function setupLikeSystem() {
    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.addEventListener("click", async function () {
            const postId = this.dataset.postId;
            const icon = this.querySelector(".like-icon");
            const counter = this.parentElement.querySelector(".likes-count");

            this.classList.add("burst");
            setTimeout(() => this.classList.remove("burst"), 350);

            const originalHtml = this.innerHTML;
            this.disabled = true;
            this.innerHTML = "⏳";

            try {
                const res = await fetch(`/like/${postId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() }
                });
                const data = await res.json();

                counter.textContent = data.likes_count;

                if (data.liked) {
                    this.classList.add("active-like");
                    icon.classList.replace("bi-hand-thumbs-up", "bi-hand-thumbs-up-fill");
                } else {
                    this.classList.remove("active-like");
                    icon.classList.replace("bi-hand-thumbs-up-fill", "bi-hand-thumbs-up");
                }

            } catch (e) {
                showToast("❌ حدث خطأ في الإعجاب");
            }

            this.disabled = false;
            this.innerHTML = originalHtml;
        });
    });
}

// ==================== نظام المشاركة ====================
function setupShareSystem() {
    const shareButtons = document.querySelectorAll(".share-btn");

    shareButtons.forEach(btn => {
        const wrapper = btn.closest(".share-wrapper");
        const menu = wrapper.querySelector(".share-options");
        const postId = btn.dataset.postId;

        // فتح/إغلاق القائمة
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            document.querySelectorAll(".share-options").forEach(m => m.classList.add("d-none"));
            menu.classList.toggle("d-none");
        });
        

        // نسخ الرابط
        wrapper.querySelector(".share-link").addEventListener("click", async () => {
            const url = `${location.origin}/#post-${postId}`;
            await navigator.clipboard.writeText(url);
            showToast("📋 تم نسخ الرابط");
        });

        // فيسبوك
        wrapper.querySelector(".share-facebook").addEventListener("click", () => {
            const url = encodeURIComponent(`${location.origin}/#post-${postId}`);
            window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, "_blank");
        });

        // تويتر
        wrapper.querySelector(".share-twitter").addEventListener("click", () => {
            const url = encodeURIComponent(`${location.origin}/#post-${postId}`);
            window.open(`https://twitter.com/intent/tweet?url=${url}`, "_blank");
        });

        // واتساب
        wrapper.querySelector(".share-whatsapp").addEventListener("click", () => {
            const url = encodeURIComponent(`${location.origin}/#post-${postId}`);
            window.open(`https://api.whatsapp.com/send?text=${url}`, "_blank");
        });

        // تيليجرام
        wrapper.querySelector(".share-telegram").addEventListener("click", () => {
            const url = encodeURIComponent(`${location.origin}/#post-${postId}`);
            window.open(`https://t.me/share/url?url=${url}`, "_blank");
        });

        // إنستغرام (لا يدعم مشاركة الروابط)
        wrapper.querySelector(".share-instagram").addEventListener("click", () => {
            showToast("⚠ إنستغرام لا يدعم المشاركة عبر الويب");
        });
    });

    // إغلاق القوائم عند الضغط خارجها
    document.addEventListener("click", () => {
        document.querySelectorAll(".share-options").forEach(m => m.classList.add("d-none"));
    });

    document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const wrapper = this.closest('.share-wrapper');
        const menu = wrapper.querySelector('.share-options');

        menu.classList.toggle('show-menu');
    });
});

// إغلاق جميع قوائم المشاركة عند الضغط خارجها
document.addEventListener("click", function (e) {
    document.querySelectorAll(".share-options.show-menu").forEach(menu => {
        if (!menu.contains(e.target) && !menu.previousElementSibling.contains(e.target)) {
            menu.classList.remove("show-menu");
        }
    });
});

document.addEventListener("click", function(e) {

    const btn = e.target.closest(".share-btn");
    if (btn) {
        e.stopPropagation();

        const menu = btn.parentElement.querySelector(".share-options");

        // إغلاق أي قائمة أخرى مفتوحة
        document.querySelectorAll(".share-options.show-menu")
            .forEach(m => m !== menu && m.classList.remove("show-menu"));

        // فتح/إغلاق القائمة الحالية
        menu.classList.toggle("show-menu");
    }
});

}


// ==================== Toast Message ====================
function showToast(message) {
    const box = document.createElement("div");
    box.className = "toast-message";
    box.textContent = message;
    Object.assign(box.style, {
        position: "fixed",
        bottom: "20px",
        right: "20px",
        background: "rgba(0,0,0,0.75)",
        color: "white",
        padding: "10px 16px",
        borderRadius: "8px",
        zIndex: 99999,
        opacity: 0,
        transition: "opacity .3s"
    });

    document.body.appendChild(box);
    setTimeout(() => box.style.opacity = 1, 10);
    setTimeout(() => {
        box.style.opacity = 0;
        setTimeout(() => box.remove(), 300);
    }, 2000);
}

// ==================== تشغيل الأنظمة ====================
document.addEventListener("DOMContentLoaded", () => {
    setupLikeSystem();
    setupShareSystem();
});
