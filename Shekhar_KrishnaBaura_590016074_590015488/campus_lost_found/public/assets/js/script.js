// public/assets/js/script.js
// Continuous, seamless right->left banner scroller.
// This JS duplicates children when needed and animates via requestAnimationFrame
// so it never pauses (even on hover). Works with the existing HTML structure:
// <div class="banner-track" id="bannerTrack"> ... items ... </div>

(function () {
  const track = document.getElementById('bannerTrack');
  if (!track) return;

  // Make sure images/resources are loaded before measuring
  function whenImagesLoaded(container, cb) {
    const imgs = Array.from(container.querySelectorAll('img'));
    if (imgs.length === 0) return cb();
    let left = imgs.length;
    imgs.forEach(img => {
      if (img.complete) {
        left -= 1;
        if (left === 0) cb();
      } else {
        img.addEventListener('load', () => {
          left -= 1;
          if (left === 0) cb();
        });
        img.addEventListener('error', () => {
          left -= 1;
          if (left === 0) cb();
        });
      }
    });
  }

  whenImagesLoaded(track, () => {
    // Remove any CSS-hover pause (ensure animation won't be paused)
    track.style.animationPlayState = 'running';

    // Duplicate content until track width >= 2x viewport width (seamless)
    const container = track.parentElement;
    const viewportW = container.clientWidth || window.innerWidth;

    // Compute current content width
    const contentWidth = track.scrollWidth;

    // If contentWidth is 0 or too small, we still duplicate at least once.
    if (contentWidth > 0) {
      // duplicate until we have enough width to scroll seamlessly
      let total = contentWidth;
      while (total < viewportW * 2) {
        // clone children
        Array.from(track.children).forEach(child => {
          const clone = child.cloneNode(true);
          clone.classList.add('duplicate-clone');
          track.appendChild(clone);
        });
        total = track.scrollWidth;
      }
    } else {
      // fallback: clone all once
      Array.from(track.children).forEach(child => {
        const clone = child.cloneNode(true);
        clone.classList.add('duplicate-clone');
        track.appendChild(clone);
      });
    }

    // Now run a JS-driven continuous scroll
    // Default speed (pixels per second)
    let pxPerSecond = 60;
    let offset = 0;
    let lastTime = performance.now();

    function step(now) {
      const dt = (now - lastTime) / 1000;
      lastTime = now;

      // continuous movement
      offset += pxPerSecond * dt;

      // Reset offset if it exceeds half of the full scroll width (since we've duplicated)
      const fullWidth = track.scrollWidth;
      if (offset >= fullWidth / 2) {
        offset = offset - fullWidth / 2;
      }

      // Apply transform
      track.style.transform = `translateX(${-offset}px)`;

      requestAnimationFrame(step);
    }

    // Ensure track has will-change for smoother animation
    track.style.willChange = 'transform';
    track.style.display = 'flex';
    track.style.flexWrap = 'nowrap';
    track.style.alignItems = 'center';

    // Start loop
    lastTime = performance.now();
    requestAnimationFrame(step);

    // Expose speed controls (optional)
    window.__bannerScroller = {
      setSpeed: s => { pxPerSecond = Number(s) || 60; }
    };
  });
})();