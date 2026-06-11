/* =========================================================
   Md Raihan Goni — portfolio interactions
   ========================================================= */
(function () {
    "use strict";

    var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Mobile nav ---------- */
    var navToggle = document.getElementById("nav-toggle");
    var nav = document.getElementById("site-nav");
    if (navToggle && nav) {
        navToggle.addEventListener("click", function () {
            var open = nav.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", String(open));
            navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        });
        nav.addEventListener("click", function (e) {
            if (e.target.tagName === "A") {
                nav.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
                navToggle.setAttribute("aria-label", "Open menu");
            }
        });
    }

    /* ---------- Footer year ---------- */
    var yearEl = document.getElementById("year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    /* ---------- Header shadow + scroll progress + neon spine ---------- */
    var header = document.getElementById("site-header");
    var progressFill = document.getElementById("scroll-progress-fill");
    var beam = document.getElementById("spine-beam");
    var ticking = false;

    function onScroll() {
        var scrollTop = window.scrollY || document.documentElement.scrollTop;
        var docH = document.documentElement.scrollHeight - window.innerHeight;
        var pct = docH > 0 ? scrollTop / docH : 0;

        if (header) header.classList.toggle("scrolled", scrollTop > 8);
        if (progressFill) progressFill.style.width = (pct * 100).toFixed(2) + "%";

        // Neon spine beam travels the full viewport height as you scroll.
        if (beam && !prefersReduced) {
            var travel = window.innerHeight + 140;
            beam.style.transform = "translateY(" + (pct * travel - 140).toFixed(1) + "px)";
        }
        ticking = false;
    }
    window.addEventListener("scroll", function () {
        if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
    }, { passive: true });
    onScroll();

    /* ---------- Reveal on scroll (staggered) ---------- */
    var reveals = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
    if (prefersReduced || !("IntersectionObserver" in window)) {
        reveals.forEach(function (el) { el.classList.add("in"); });
    } else {
        // Stagger items that share a parent for a sequenced entrance.
        var groups = {};
        reveals.forEach(function (el) {
            var parent = el.parentElement;
            var key = parent ? (parent.className || "x") : "x";
            groups[key] = groups[key] || [];
            if (el.matches(".card, .pub, .tl-item, .chips, .skill-group") || el.parentElement.matches(".award-list")) {
                el.style.setProperty("--d", (groups[key].length * 70) + "ms");
            }
            groups[key].push(el);
        });

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in");
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
        reveals.forEach(function (el) { io.observe(el); });
    }

    /* ---------- Animated stat counters ---------- */
    var counters = Array.prototype.slice.call(document.querySelectorAll(".stat-num[data-count]"));
    function animateCount(el) {
        var target = parseInt(el.getAttribute("data-count"), 10) || 0;
        if (prefersReduced) { el.textContent = String(target); return; }
        var start = performance.now();
        var dur = 1100;
        function step(now) {
            var t = Math.min((now - start) / dur, 1);
            var eased = 1 - Math.pow(1 - t, 3);
            el.textContent = String(Math.round(eased * target));
            if (t < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }
    if ("IntersectionObserver" in window && counters.length) {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) { animateCount(entry.target); co.unobserve(entry.target); }
            });
        }, { threshold: 0.6 });
        counters.forEach(function (el) { co.observe(el); });
    } else {
        counters.forEach(function (el) { el.textContent = el.getAttribute("data-count"); });
    }

    /* ---------- Active nav link (scroll spy) ---------- */
    var navLinks = Array.prototype.slice.call(document.querySelectorAll(".site-nav a"));
    var sections = navLinks
        .map(function (a) { return document.querySelector(a.getAttribute("href")); })
        .filter(Boolean);

    if ("IntersectionObserver" in window && sections.length) {
        var spy = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var id = entry.target.id;
                    navLinks.forEach(function (a) {
                        a.classList.toggle("active", a.getAttribute("href") === "#" + id);
                    });
                }
            });
        }, { threshold: 0.4, rootMargin: "-45% 0px -45% 0px" });
        sections.forEach(function (s) { spy.observe(s); });
    }

    /* ---------- Publication tabs (Journals / Conferences) ---------- */
    var pubTabs = Array.prototype.slice.call(document.querySelectorAll(".pub-tab"));
    var pubPanels = {
        journals: document.getElementById("panel-journals"),
        conferences: document.getElementById("panel-conferences")
    };
    function selectPubTab(target) {
        pubTabs.forEach(function (tab) {
            var on = tab.getAttribute("data-target") === target;
            tab.classList.toggle("active", on);
            tab.setAttribute("aria-selected", String(on));
        });
        Object.keys(pubPanels).forEach(function (key) {
            if (pubPanels[key]) pubPanels[key].hidden = key !== target;
        });
    }
    pubTabs.forEach(function (tab) {
        tab.addEventListener("click", function () { selectPubTab(tab.getAttribute("data-target")); });
    });
})();
