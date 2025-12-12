/**
 * Detective Study Helper - Internationalization Module
 * i18n Core Module for Chinese/English Language Support
 */

const I18n = {
    // Supported languages
    SUPPORTED_LANGS: ['zh-CN', 'en-US'],
    DEFAULT_LANG: 'zh-CN',
    STORAGE_KEY: 'detective_helper_lang',
    COOKIE_NAME: 'lang',

    // Current language
    currentLang: null,

    // Translation dictionaries cache
    translations: {},

    /**
     * Initialize i18n module
     */
    init() {
        // Load translation dictionaries
        this.translations = {
            'zh-CN': window.translations_zh || {},
            'en-US': window.translations_en || {}
        };

        // Get current language
        this.currentLang = this.getStoredLang() || this.DEFAULT_LANG;

        // Sync to cookie for backend
        this.setCookie(this.COOKIE_NAME, this.currentLang);

        // Apply language
        this.applyLanguage(this.currentLang);

        // Initialize language switcher buttons
        this.initLanguageSwitcher();

        console.log('[i18n] Initialized with language:', this.currentLang);
        return this;
    },

    /**
     * Get stored language setting
     */
    getStoredLang() {
        // Priority: localStorage > Cookie
        const stored = localStorage.getItem(this.STORAGE_KEY);
        if (stored && this.SUPPORTED_LANGS.includes(stored)) {
            return stored;
        }

        // Try getting from Cookie
        const cookie = this.getCookie(this.COOKIE_NAME);
        if (cookie && this.SUPPORTED_LANGS.includes(cookie)) {
            return cookie;
        }

        return null;
    },

    /**
     * Get Cookie value
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    },

    /**
     * Set Cookie
     */
    setCookie(name, value, days = 365) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    },

    /**
     * Switch language
     */
    switchLanguage(lang) {
        if (!this.SUPPORTED_LANGS.includes(lang)) {
            console.warn('[i18n] Unsupported language:', lang);
            return;
        }

        if (lang === this.currentLang) {
            return; // No change needed
        }

        this.currentLang = lang;

        // Save to localStorage
        localStorage.setItem(this.STORAGE_KEY, lang);

        // Sync to Cookie (for backend)
        this.setCookie(this.COOKIE_NAME, lang);

        console.log('[i18n] Language switched to:', lang);

        // Refresh page to apply new language
        location.reload();
    },

    /**
     * Apply language to page
     */
    applyLanguage(lang) {
        // Set HTML lang attribute
        document.documentElement.lang = lang;

        // Translate all elements with data-i18n attributes
        this.translatePage();

        // Update language switcher button state
        this.updateSwitcherState(lang);
    },

    /**
     * Translate page elements
     */
    translatePage() {
        // Translate element content
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation && translation !== key) {
                el.textContent = translation;
            }
        });

        // Translate placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation && translation !== key) {
                el.placeholder = translation;
            }
        });

        // Translate title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            const translation = this.t(key);
            if (translation && translation !== key) {
                el.title = translation;
            }
        });

        // Translate page title
        const pageTitleEl = document.querySelector('[data-i18n-page-title]');
        if (pageTitleEl) {
            const key = pageTitleEl.getAttribute('data-i18n-page-title');
            const translation = this.t(key);
            if (translation && translation !== key) {
                document.title = translation;
            }
        }

        // Translate HTML content (innerHTML)
        document.querySelectorAll('[data-i18n-html]').forEach(el => {
            const key = el.getAttribute('data-i18n-html');
            const translation = this.t(key);
            if (translation && translation !== key) {
                el.innerHTML = translation;
            }
        });
    },

    /**
     * Get translation text
     * @param {string} key - Dot-separated key path, e.g., "home.hero.title1"
     * @param {object} params - Interpolation parameters
     * @returns {string} Translated text or original key if not found
     */
    t(key, params = {}) {
        const dict = this.translations[this.currentLang];
        if (!dict) return key;

        // Navigate nested object by dot-separated path
        const keys = key.split('.');
        let value = dict;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return key; // Translation not found, return original key
            }
        }

        // Handle string interpolation
        if (typeof value === 'string' && Object.keys(params).length > 0) {
            Object.keys(params).forEach(param => {
                value = value.replace(new RegExp(`{{${param}}}`, 'g'), params[param]);
            });
        }

        return value;
    },

    /**
     * Initialize language switcher buttons
     */
    initLanguageSwitcher() {
        // Find all language switcher containers
        document.querySelectorAll('.lang-switcher').forEach(switcher => {
            switcher.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-lang]');
                if (btn) {
                    const lang = btn.getAttribute('data-lang');
                    this.switchLanguage(lang);
                }
            });
        });

        // Also handle individual lang buttons outside containers
        document.querySelectorAll('[data-lang]').forEach(btn => {
            if (!btn.closest('.lang-switcher')) {
                btn.addEventListener('click', () => {
                    const lang = btn.getAttribute('data-lang');
                    this.switchLanguage(lang);
                });
            }
        });
    },

    /**
     * Update language switcher button state
     */
    updateSwitcherState(lang) {
        document.querySelectorAll('[data-lang]').forEach(btn => {
            const btnLang = btn.getAttribute('data-lang');
            if (btnLang === lang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    },

    /**
     * Get current language
     */
    getCurrentLang() {
        return this.currentLang;
    },

    /**
     * Check if current language is Chinese
     */
    isChinese() {
        return this.currentLang === 'zh-CN';
    },

    /**
     * Check if current language is English
     */
    isEnglish() {
        return this.currentLang === 'en-US';
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.i18n = I18n.init();
});

// Also expose I18n object globally
window.I18n = I18n;
