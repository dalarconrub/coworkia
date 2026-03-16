// Forzar tamaño del logo y ocultar texto MAR
(function() {
    function applyLogoStyles() {
        // Ocultar texto del título
        const title = document.querySelector('.md-header__title');
        if (title) {
            title.style.cssText = 'display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; overflow: hidden !important;';
        }
        
        const topic = document.querySelector('.md-header__topic');
        if (topic) {
            topic.style.cssText = 'display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; overflow: hidden !important;';
        }
        
        // Aumentar tamaño del logo y centrarlo
        const logo = document.querySelector('.md-header__button.md-logo');
        if (logo) {
            logo.style.cssText = 'position: absolute !important; left: 50% !important; transform: translateX(-50%) !important; padding: 0.5rem 1.5rem !important; margin: 0 !important; z-index: 10 !important; display: flex !important; align-items: center !important; justify-content: center !important; cursor: default !important; pointer-events: none !important;';
            
            // Prevenir el comportamiento de click
            logo.href = '#';
            logo.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            };
            
            // También prevenir eventos de forma más agresiva
            logo.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                return false;
            }, true);
        }
        
        const logoImg = document.querySelector('.md-header__button.md-logo img, .md-header__button.md-logo svg');
        if (logoImg) {
            logoImg.style.cssText = 'height: 10rem !important; width: auto !important; max-width: none !important; display: block !important; margin: 0 !important; object-fit: contain !important; pointer-events: none !important;';
        }
        
        // Ajustar header para dar más espacio al logo
        const header = document.querySelector('.md-header');
        if (header) {
            header.style.cssText = 'min-height: 11rem !important; padding: 1rem 0 !important; display: flex !important; align-items: center !important; justify-content: center !important; position: relative !important;';
        }
        
        const headerInner = document.querySelector('.md-header__inner');
        if (headerInner) {
            headerInner.style.cssText = 'justify-content: center !important; position: relative !important; padding: 0 !important; align-items: center !important; width: 100% !important;';
        }
    }
    
    // Ejecutar inmediatamente y también cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyLogoStyles);
    } else {
        applyLogoStyles();
    }
    
    // También ejecutar después de un pequeño delay para asegurar que se aplique
    setTimeout(applyLogoStyles, 100);
    setTimeout(applyLogoStyles, 500);
})();
