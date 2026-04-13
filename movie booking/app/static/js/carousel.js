/* ==================== CAROUSEL FUNCTIONALITY ==================== */

let carouselPosition = 0;

function moveCarousel(direction) {
    const track = document.getElementById('carouselTrack');
    const slides = document.querySelectorAll('.carousel-slide');
    
    if (slides.length === 0) return;

    const slideWidth = slides[0].offsetWidth + 24; // 24px gap
    const maxPosition = -(slideWidth * (slides.length - 4));

    carouselPosition += direction * slideWidth;
    
    // Constrain position
    if (carouselPosition > 0) {
        carouselPosition = 0;
    }
    if (carouselPosition < maxPosition) {
        carouselPosition = maxPosition;
    }

    track.style.transform = `translateX(${carouselPosition}px)`;
    showToast('Carousel moved', 'info', 1500);
}

// Touch support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('DOMContentLoaded', function() {
    const track = document.getElementById('carouselTrack');
    if (track) {
        track.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });

        track.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    }
});

function handleSwipe() {
    const swipeThreshold = 50;
    if (touchStartX - touchEndX > swipeThreshold) {
        moveCarousel(1); // Swipe left
    }
    if (touchEndX - touchStartX > swipeThreshold) {
        moveCarousel(-1); // Swipe right
    }
}

// Auto-scroll carousel
function autoScroll() {
    setInterval(() => {
        const track = document.getElementById('carouselTrack');
        if (track && document.hidden === false) {
            moveCarousel(1);
        }
    }, 5000); // Change slide every 5 seconds
}

// Initialize carousel
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        autoScroll();
    });
} else {
    autoScroll();
}
