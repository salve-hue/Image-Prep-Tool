# -*- coding: utf-8 -*-
"""
Transforms playmat-designer-v1.7.1.liquid into standalone index.html
Run: python build.py
"""
import re, os, sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC  = r'C:\Users\Brian\Downloads\playmat-designer-v1.7.1.liquid'
DEST = r'C:\Users\Brian\Downloads\playmat-studio\index.html'

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()

# ── helpers ───────────────────────────────────────────────────────────────────
def rb(text, start, end, repl=''):
    """Remove or replace text from start up to and including end."""
    s = text.find(start)
    if s == -1:
        print(f'  [WARN] start not found: {repr(start[:60])}')
        return text
    e = text.find(end, s)
    if e == -1:
        print(f'  [WARN] end not found: {repr(end[:60])}')
        return text
    return text[:s] + repl + text[e + len(end):]

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 – REMOVALS
# ══════════════════════════════════════════════════════════════════════════════

# 1a. CloudFlare email decode script
src = src.replace(
    '<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script>',
    ''
)
print('1a. Removed CF email decode script')

# 1b. Liquid __PM_DEFAULT_VARIANT_ID__ line
src = re.sub(r'[ \t]*window\.__PM_DEFAULT_VARIANT_ID__[^\n]+\n', '', src)
print('1b. Removed Liquid __PM_DEFAULT_VARIANT_ID__')

# 1c. Shopify schema block
src = rb(src, '{% schema %}', '{% endschema %}')
print('1c. Removed schema block')

# 1d-1h. Remove PRODUCT_SIZE_MAP, ALWAYS_SHOW_PRODUCT_IDS, getPageVariant, getPageQty in one block
# End marker includes 'const LAYOUT_RAW' so repl injects it back
src = rb(src,
    '\n    // PRODUCT_SIZE_MAP: maps Shopify product ID',
    '\n    }\n\n    const LAYOUT_RAW',
    '\n    const LAYOUT_RAW'
)
print('1d-1h. Removed PRODUCT_SIZE_MAP + ALWAYS_SHOW + getPageVariant + getPageQty')

# 1f. BUNDLE_CONFIG line
src = re.sub(r'[ \t]*window\.BUNDLE_CONFIG\s*=\s*\{[^\n]+\};\s*\n', '', src)
print('1f. Removed BUNDLE_CONFIG')

# 1i. Replace buildPrintFilename with simple version
src = rb(src,
    '\n    // Build a structured print file filename:',
    '\n    };\n\n    async function uploadImageToStaging',
    '''
    window.buildPrintFilename = function() {
        return 'playmat-' + APP.activeSizeKey + '-' + Date.now() + '.jpg';
    };

    async function uploadImageToStaging'''
)
print('1i. Replaced buildPrintFilename')

# 1j. Replace _origShowSimple + _applyNavOffsetToSimple block
#     (the original calls getNavHeight which we're removing)
src = rb(src,
    '\n    // Called when the file input resolves',
    '\n    };\n\n    // Measure the tallest fixed/sticky element',
    '''
    window._applyNavOffsetToSimple = function() {
        var bd = document.getElementById('simple-backdrop');
        bd.style.setProperty('--adv-nav-offset', '0px');
    };

    // Measure the tallest fixed/sticky element'''
)
print('1g. Replaced _applyNavOffsetToSimple (removed _origShowSimple + getNavHeight ref)')

# 1k. Remove getNavHeight function
src = rb(src,
    'tallest fixed/sticky element above the fold (the nav bar).\n    // Returns at least 80px',
    '\n    };\n\n    window.restartApp',
    '\n    window.restartApp'
)
print('1k. Removed getNavHeight')

# 1l. Fix triggerAdvancedFlow nav offset
src = src.replace(
    "advBd.style.setProperty('--adv-nav-offset', isMobile ? '0px' : window.getNavHeight() + 'px');",
    "advBd.style.setProperty('--adv-nav-offset', '20px');"
)
print('1l. Fixed triggerAdvancedFlow nav offset')

# 1m. Replace initDesignerVisibility with simple always-show version
src = rb(src,
    '\n    window.initDesignerVisibility = async function() {',
    '\n    };\n\n    // --- DPI CHECKER ---',
    '''
    window.initDesignerVisibility = function() {
        document.getElementById('designer-visibility-wrapper').style.display = '';
        window.updateInfoBars(null);
        window.populateGameDropdowns();
    };

    // --- DPI CHECKER ---'''
)
print('1m. Replaced initDesignerVisibility')

# 1n. Remove submitSimpleCart + submitToCart + _executeCart block
src = rb(src,
    '\n    // ============================================================\n    // FIX 3 (CODE QUALITY): submitToCart broken into named steps',
    '\n    };\n\n    // Injects 300 DPI metadata',
    '\n\n    // Injects 300 DPI metadata'
)
print('1n. Removed submitSimpleCart / submitToCart / _executeCart')

# 1o. Remove pushToShopifyCart (repl restores the comment heading)
src = rb(src,
    '\n    async function pushToShopifyCart(',
    '\n    }\n\n    // --- COLOR SYNC HELPERS',
    '\n\n    // --- COLOR SYNC HELPERS'
)
print('1o. Removed pushToShopifyCart')

# 1p. Clean up help modal — replace form + socials with simple message
# Find the help modal p tag through to the end of the social-row div
src = rb(src,
    "        <p style=\"color:var(--brand-text-sec); font-size:13px; margin-bottom:20px;\">Need help ensuring your art prints perfectly?",
    "        </div>\n    </div>\n</div>\n\n\n<div id=\"bleed-confirm-modal\"",
    "        <p style=\"color:var(--brand-text-sec); font-size:13px; margin-bottom:10px;\">For support and documentation, visit the project on GitHub.</p>\n    </div>\n</div>\n\n\n<div id=\"bleed-confirm-modal\""
)
print('1p. Cleaned help modal (removed Shopify form + social links)')

# 1q. Fix restartApp file input references to be safe
src = src.replace(
    "        document.getElementById('adv-file-in').value    = '';\n        document.getElementById('simple-file-in').value = '';",
    "        var _afi = document.getElementById('adv-file-in'); if(_afi) _afi.value='';\n        var _sfi = document.getElementById('simple-file-in'); if(_sfi) _sfi.value='';"
)
print('1q. Fixed restartApp file inputs')

# 1r. Clean stale comment references to removed functions
src = src.replace(
    '// Liquid-injected fallback variant ID — used by getPageVariant() for single-variant',
    '// Liquid-injected fallback variant ID (Shopify) — removed in standalone build'
)
src = src.replace(
    '// Variant ID and quantity are read live from the page at cart time via getPageVariant()/get',
    '// (Shopify cart integration removed in standalone build)'
)
src = src.replace(
    '// Previously duplicated between renderLayout and submitToCart.',
    '// Previously duplicated between renderLayout and the cart flow.'
)
src = src.replace(
    '// FIX 6: Correct radius formula — was (cx*cx + cy*cy) in submitToCart, now unified',
    '// FIX 6: Correct radius formula — was (cx*cx + cy*cy) in the old cart path, now unified'
)
print('1r. Cleaned stale comment references')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 – MODIFY HTML
# ══════════════════════════════════════════════════════════════════════════════

# 2a. Update landing paragraph
src = src.replace(
    '<p style="color: #444; font-size: 14px; margin-bottom: 30px;">Select your edge style above, then upload your work below.</p>',
    '<p style="color: #888; font-size: 14px; margin-bottom: 30px;">Select your mat size, then choose an editor or tool below.</p>'
)
print('2a. Updated landing paragraph')

# 2b. Add size selector + tool buttons to landing page
OLD_LANDING = (
    '        <span class="landing-label" style="color: var(--brand-hover);">CHOOSE EDITOR</span>\n'
    '        <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">\n'
    '            <button class="action-btn btn-landing-simple" style="max-width: 200px; padding: 15px;" onclick="window.triggerSimpleFlow()">QUICK UPLOAD</button>\n'
    '            <button class="action-btn btn-landing-adv" style="max-width: 200px; padding: 15px;" onclick="window.triggerAdvancedFlow()">ADVANCED EDITOR</button>\n'
    '        </div>'
)
NEW_LANDING = """        <span class="landing-label" style="color: var(--brand-hover);">MAT SIZE</span>
        <select id="standalone-size-sel" class="ui-select"
            style="max-width:320px; margin:0 auto 24px; display:block;"
            onchange="APP.activeSizeKey=this.value; window.populateGameDropdowns(); window.updateInfoBars(null);">
            <option value="standard">Standard 24&Prime; &times; 14&Prime;</option>
            <option value="extended">Extended 28&Prime; &times; 14&Prime;</option>
            <option value="victor">Victor Deskmat 24&Prime; &times; 12&Prime;</option>
            <option value="secundus">Secundus Deskmat 28&Prime; &times; 12&Prime;</option>
            <option value="primus">Primus Deskmat 31&Prime; &times; 12&Prime;</option>
            <option value="tiro">Tiro Mousepad 10&Prime; &times; 8&Prime;</option>
            <option value="veteranus">Veteranus Mousepad 12.5&Prime; &times; 10.5&Prime;</option>
            <option value="gladiator">Gladiator Mousepad 18&Prime; &times; 12&Prime;</option>
        </select>

        <div class="tool-tab-bar">
            <button class="tool-tab-btn active" data-tab="quick-upload" onclick="window.switchTab('quick-upload')">&#x26A1; QUICK UPLOAD</button>
            <button class="tool-tab-btn" data-tab="adv-editor" onclick="window.switchTab('adv-editor')">&#x270F;&#xFE0F; ADVANCED EDITOR</button>
            <button class="tool-tab-btn" data-tab="batch" onclick="window.switchTab('batch')">&#x1F5BC;&#xFE0F; BATCH ENHANCE</button>
            <button class="tool-tab-btn" data-tab="converter" onclick="window.switchTab('converter')">&#x1F504; FORMAT CONVERTER</button>
        </div>

        <!-- Quick Upload -->
        <div id="tab-panel-quick-upload" class="tool-tab-panel active">
            <div style="text-align:center; padding:36px 20px;">
                <div style="font-size:48px; margin-bottom:14px;">&#x26A1;</div>
                <h3 style="color:var(--brand-hover); margin:0 0 10px; font-size:18px; text-transform:uppercase; letter-spacing:1px;">Quick Upload</h3>
                <p style="color:var(--brand-text-sec); font-size:13px; margin:0 auto 26px; max-width:360px; line-height:1.6;">Upload your artwork, fit it to the selected mat size, apply optional color correction, and download a print-ready JPG.</p>
                <button class="action-btn btn-landing-simple" style="max-width:220px; padding:16px; font-size:15px;" onclick="window.triggerSimpleFlow()">OPEN EDITOR &#x2192;</button>
            </div>
        </div>

        <!-- Advanced Editor -->
        <div id="tab-panel-adv-editor" class="tool-tab-panel">
            <div style="text-align:center; padding:36px 20px;">
                <div style="font-size:48px; margin-bottom:14px;">&#x270F;&#xFE0F;</div>
                <h3 style="color:var(--brand-hover); margin:0 0 10px; font-size:18px; text-transform:uppercase; letter-spacing:1px;">Advanced Editor</h3>
                <p style="color:var(--brand-text-sec); font-size:13px; margin:0 auto 26px; max-width:360px; line-height:1.6;">Full canvas editor with AI upscaling, frame break, game overlay templates, recolor brush, and precise positioning controls.</p>
                <button class="action-btn btn-landing-adv" style="max-width:220px; padding:16px; font-size:15px;" onclick="window.triggerAdvancedFlow()">OPEN EDITOR &#x2192;</button>
            </div>
        </div>

        <!-- Batch Enhance -->
        <div id="tab-panel-batch" class="tool-tab-panel">
            <div id="batch-drop-zone"
                style="border:2px dashed rgba(255,255,255,0.25); border-radius:8px; padding:40px 20px; text-align:center; cursor:pointer; margin-bottom:20px; transition:border-color 0.2s;"
                ondragover="event.preventDefault(); this.style.borderColor='var(--brand-hover)';"
                ondragleave="this.style.borderColor='rgba(255,255,255,0.25)';"
                ondrop="event.preventDefault(); this.style.borderColor='rgba(255,255,255,0.25)'; window.handleBatchFiles(event.dataTransfer.files);"
                onclick="document.getElementById('batch-file-in').click()">
                <div style="font-size:40px; margin-bottom:10px;">&#x1F5BC;&#xFE0F;</div>
                <p style="color:var(--brand-text-pri); font-size:16px; margin:0 0 6px; font-weight:600;">Drag &amp; drop images here</p>
                <p style="color:var(--brand-text-sec); font-size:12px; margin:0;">or click to select multiple files</p>
                <p style="color:var(--brand-text-sec); font-size:11px; margin:8px 0 0; opacity:0.7;">Applies: Brightness +12% &middot; Contrast +8% &middot; Saturation +15% &middot; Exports as 99% JPG</p>
            </div>
            <input type="file" id="batch-file-in" accept="image/*" multiple style="display:none;" onchange="window.handleBatchFiles(this.files)">
            <div id="batch-status" style="display:none; color:var(--brand-hover); font-size:13px; margin-bottom:12px; text-align:center;"></div>
            <div id="batch-preview-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(150px,1fr)); gap:12px; margin-bottom:20px;"></div>
            <div id="batch-controls" style="display:none; border-top:1px solid rgba(255,255,255,0.1); padding-top:20px;">
                <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                    <button id="batch-download-btn" class="action-btn" style="width:auto; padding:14px 32px; font-size:15px;">&#x2B07; DOWNLOAD</button>
                    <button class="action-btn btn-secondary" style="width:auto; padding:14px 20px; margin:0;" onclick="window.clearBatch()">CLEAR</button>
                </div>
            </div>
        </div>

        <!-- Format Converter -->
        <div id="tab-panel-converter" class="tool-tab-panel">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
                <span style="color:var(--brand-text-sec); font-size:12px; font-weight:bold; letter-spacing:1px; white-space:nowrap;">CONVERT TO:</span>
                <select id="converter-format-sel" class="ui-select" style="width:auto; min-width:200px; padding:8px 12px; font-size:13px;">
                    <option value="jpeg">JPG &mdash; 99% quality</option>
                    <option value="png">PNG &mdash; lossless</option>
                    <option value="webp">WEBP &mdash; 95% quality</option>
                </select>
            </div>
            <div id="converter-drop-zone"
                style="border:2px dashed rgba(255,255,255,0.25); border-radius:8px; padding:40px 20px; text-align:center; cursor:pointer; margin-bottom:20px; transition:border-color 0.2s;"
                ondragover="event.preventDefault(); this.style.borderColor='var(--brand-hover)';"
                ondragleave="this.style.borderColor='rgba(255,255,255,0.25)';"
                ondrop="event.preventDefault(); this.style.borderColor='rgba(255,255,255,0.25)'; window.handleConverterFiles(event.dataTransfer.files);"
                onclick="document.getElementById('converter-file-in').click()">
                <div style="font-size:40px; margin-bottom:10px;">&#x1F504;</div>
                <p style="color:var(--brand-text-pri); font-size:16px; margin:0 0 6px; font-weight:600;">Drag &amp; drop images to convert</p>
                <p style="color:var(--brand-text-sec); font-size:12px; margin:0;">PNG &middot; WEBP &middot; GIF &middot; AVIF &middot; BMP &middot; JPG &#x2192; any format</p>
            </div>
            <input type="file" id="converter-file-in" accept="image/*" multiple style="display:none;" onchange="window.handleConverterFiles(this.files)">
            <div id="converter-status" style="display:none; color:var(--brand-hover); font-size:13px; margin-bottom:12px; text-align:center;"></div>
            <div id="converter-preview-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(150px,1fr)); gap:12px; margin-bottom:20px;"></div>
            <div id="converter-controls" style="display:none; border-top:1px solid rgba(255,255,255,0.1); padding-top:20px;">
                <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                    <button id="converter-download-btn" class="action-btn" style="width:auto; padding:14px 32px; font-size:15px;" onclick="window.downloadConverted()">&#x2B07; DOWNLOAD</button>
                    <button class="action-btn btn-secondary" style="width:auto; padding:14px 20px; margin:0;" onclick="window.clearConverter()">CLEAR</button>
                </div>
            </div>
        </div>"""
src = src.replace(OLD_LANDING, NEW_LANDING)
print('2b. Built tab interface (Quick Upload / Adv Editor / Batch / Converter)')

# 2c. Change ADD TO CART -> DOWNLOAD buttons
src = src.replace(
    'onclick="window.submitSimpleCart()">ADD TO CART</button>',
    "onclick=\"window.downloadDesign('simple')\">DOWNLOAD</button>"
)
src = src.replace(
    "onclick=\"window.submitToCart('adv')\">ADD TO CART</button>",
    "onclick=\"window.downloadDesign('adv')\">DOWNLOAD</button>"
)
print('2c. Changed Add to Cart -> Download buttons')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 – ADD NEW HTML SECTIONS (batch + converter backdrops)
# ══════════════════════════════════════════════════════════════════════════════

# Step 3: Batch/converter HTML now lives inside the tab panels in NEW_LANDING above.
# No separate backdrop overlays needed.
print('3. Batch + converter live in tab panels (no separate backdrops)')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 – NEW JS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

NEW_JS = """
    // ============================================================
    // DOWNLOAD (replaces Add to Cart)
    // ============================================================
    window.downloadDesign = async function(mode) {
        var isAdv        = (mode === 'adv');
        var btn          = isAdv ? document.getElementById('sidebar-atc') : document.getElementById('simple-atc');
        var activeCanvas = isAdv ? window.canvas : window.sCanvas;

        if (!activeCanvas.getObjects().find(function(o){ return o.name === 'art'; }) && !activeCanvas.backgroundColor) {
            window.showAppAlert("Missing Artwork", "Please upload artwork before downloading.", "error");
            return;
        }

        if (!window.checkArtCoverage(activeCanvas)) {
            APP._bleedConfirmCallback = function() { window._executeDownload(mode, btn, activeCanvas); };
            document.getElementById('bleed-confirm-modal').style.display = 'flex';
            return;
        }

        await window._executeDownload(mode, btn, activeCanvas);
    };

    window._executeDownload = async function(mode, btn, activeCanvas) {
        var isAdv    = (mode === 'adv');
        var origText = btn.innerText;
        btn.innerText = 'PREPARING...'; btn.disabled = true;
        try {
            var blob     = await buildPrintCanvas(isAdv, activeCanvas);
            var filename = window.buildPrintFilename();
            var url      = URL.createObjectURL(blob);
            var a        = document.createElement('a');
            a.href = url; a.download = filename;
            document.body.appendChild(a); a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            btn.innerText = 'DOWNLOADED! \u2713'; btn.style.background = 'var(--success-green)';
            setTimeout(function() {
                btn.innerText = 'DOWNLOAD';
                btn.style.background = 'var(--brand-primary)';
                btn.disabled = false;
            }, 2500);
        } catch(err) {
            console.error(err);
            window.showAppAlert("Download Error", err.message || "An error occurred. Please try again.", "error");
            btn.innerText = origText; btn.style.background = 'var(--brand-primary)'; btn.disabled = false;
        }
    };

    // ============================================================
    // BATCH ENHANCE MODE
    // ============================================================
    var _batch = { results: [] };

    // ── TAB NAVIGATION ──────────────────────────────────────────
    window.switchTab = function(tabId) {
        document.querySelectorAll('.tool-tab-btn').forEach(function(b) {
            b.classList.toggle('active', b.dataset.tab === tabId);
        });
        document.querySelectorAll('.tool-tab-panel').forEach(function(p) {
            p.classList.remove('active');
        });
        var panel = document.getElementById('tab-panel-' + tabId);
        if (panel) panel.classList.add('active');
    };

    window.openBatchMode = function() { window.switchTab('batch'); };
    window.closeBatchMode = function() { /* tools now live in tabs — no overlay to close */ };

    window.clearBatch = function() {
        _batch.results = [];
        document.getElementById('batch-preview-grid').innerHTML = '';
        document.getElementById('batch-controls').style.display = 'none';
        document.getElementById('batch-status').style.display = 'none';
        document.getElementById('batch-file-in').value = '';
    };

    window.handleBatchFiles = async function(files) {
        if (!files || files.length === 0) return;
        var statusEl = document.getElementById('batch-status');
        var gridEl   = document.getElementById('batch-preview-grid');
        statusEl.style.display = 'block';
        statusEl.textContent   = 'Processing 0 / ' + files.length + '...';

        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            statusEl.textContent = 'Processing ' + (i + 1) + ' / ' + files.length + ': ' + file.name;
            try {
                var blob     = await window._applyBatchEnhancement(file);
                var baseName = file.name.replace(/\\.[^.]+$/, '');
                var outName  = baseName + '-enhanced.jpg';
                var thumbUrl = URL.createObjectURL(blob);
                var idx      = _batch.results.length;
                _batch.results.push({ name: outName, blob: blob, thumbUrl: thumbUrl });

                var card = document.createElement('div');
                card.style.cssText = 'background:rgba(0,0,0,0.3);border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.1);text-align:center;';
                card.innerHTML =
                    '<img src="' + thumbUrl + '" style="width:100%;height:100px;object-fit:cover;display:block;">' +
                    '<div style="padding:6px 6px 2px;font-size:10px;color:var(--brand-text-sec);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + outName + '">' + outName + '</div>' +
                    '<div style="padding:2px 6px 6px;display:flex;justify-content:space-between;align-items:center;">' +
                    '<span style="font-size:10px;color:var(--success-green);font-weight:bold;">\u2713 ENHANCED</span>' +
                    '<button onclick="window.downloadBatchSingle(' + idx + ')" style="background:none;border:none;color:var(--brand-hover);cursor:pointer;font-size:15px;padding:2px 4px;line-height:1;" title="Download this file">\u2B07</button>' +
                    '</div>';
                gridEl.appendChild(card);
            } catch(err) {
                console.error('Batch error for', file.name, err);
                var errCard = document.createElement('div');
                errCard.style.cssText = 'background:rgba(255,71,87,0.15);border-radius:6px;padding:10px;border:1px solid rgba(255,71,87,0.3);text-align:center;';
                errCard.innerHTML = '<div style="font-size:10px;color:var(--danger-red);">\u2717 ' + file.name + '<br>Failed</div>';
                gridEl.appendChild(errCard);
            }
        }

        statusEl.textContent = 'Done! ' + _batch.results.length + ' image(s) ready.';
        if (_batch.results.length > 0) {
            var dlBtn = document.getElementById('batch-download-btn');
            if (_batch.results.length === 1) {
                dlBtn.textContent = '\u2B07 DOWNLOAD';
                dlBtn.onclick = function() { window.downloadBatchSingle(0); };
            } else {
                dlBtn.textContent = '\u2B07 DOWNLOAD ALL AS ZIP';
                dlBtn.onclick = window.downloadBatchZip;
            }
            document.getElementById('batch-controls').style.display = 'block';
        }
    };

    window._applyBatchEnhancement = function(file) {
        return new Promise(function(resolve, reject) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var img = new Image();
                img.onload = function() {
                    var c    = document.createElement('canvas');
                    c.width  = img.naturalWidth  || img.width;
                    c.height = img.naturalHeight || img.height;
                    var ctx  = c.getContext('2d');
                    ctx.filter = 'brightness(112%) contrast(108%) saturate(115%)';
                    ctx.drawImage(img, 0, 0);
                    c.toBlob(function(b) {
                        if (b) resolve(b); else reject(new Error('Canvas export failed'));
                    }, 'image/jpeg', 0.99);
                };
                img.onerror = function() { reject(new Error('Failed to load image')); };
                img.src = e.target.result;
            };
            reader.onerror = function() { reject(new Error('Failed to read file')); };
            reader.readAsDataURL(file);
        });
    };

    window.downloadBatchSingle = function(idx) {
        var r = _batch.results[idx];
        if (!r) return;
        var url = URL.createObjectURL(r.blob);
        var a   = document.createElement('a');
        a.href = url; a.download = r.name;
        document.body.appendChild(a); a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    window.downloadBatchZip = async function() {
        if (_batch.results.length === 0) return;
        var btn = document.getElementById('batch-download-btn');
        var origLabel = btn.textContent;
        btn.textContent = 'ZIPPING...'; btn.disabled = true;
        try {
            var zip = new JSZip();
            _batch.results.forEach(function(r) { zip.file(r.name, r.blob); });
            var zipBlob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 3 } });
            var url = URL.createObjectURL(zipBlob);
            var a   = document.createElement('a');
            a.href = url; a.download = 'playmat-enhanced-' + Date.now() + '.zip';
            document.body.appendChild(a); a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            btn.textContent = 'DOWNLOADED! \u2713'; btn.style.background = 'var(--success-green)';
            setTimeout(function() { btn.textContent = origLabel; btn.style.background = ''; btn.disabled = false; }, 2500);
        } catch(err) {
            console.error(err);
            window.showAppAlert("ZIP Error", "Failed to create ZIP. Please try again.", "error");
            btn.textContent = origLabel; btn.disabled = false;
        }
    };

    // ============================================================
    // FORMAT CONVERTER MODE
    // ============================================================
    var _converter = { results: [] };

    window.openConverterMode = function() { window.switchTab('converter'); };
    window.closeConverterMode = function() { /* tools now live in tabs — no overlay to close */ };

    window.clearConverter = function() {
        _converter.results = [];
        document.getElementById('converter-preview-grid').innerHTML = '';
        document.getElementById('converter-controls').style.display = 'none';
        document.getElementById('converter-status').style.display = 'none';
        document.getElementById('converter-file-in').value = '';
    };

    // Maps format value -> { mimeType, quality, ext, label }
    var _fmtMap = {
        'jpeg': { mimeType: 'image/jpeg', quality: 0.99, ext: 'jpg',  label: 'JPG'  },
        'png':  { mimeType: 'image/png',  quality: 1.0,  ext: 'png',  label: 'PNG'  },
        'webp': { mimeType: 'image/webp', quality: 0.95, ext: 'webp', label: 'WEBP' }
    };

    window.handleConverterFiles = async function(files) {
        if (!files || files.length === 0) return;
        var fmtKey   = (document.getElementById('converter-format-sel') || {}).value || 'jpeg';
        var fmt      = _fmtMap[fmtKey] || _fmtMap['jpeg'];
        var statusEl = document.getElementById('converter-status');
        var gridEl   = document.getElementById('converter-preview-grid');
        statusEl.style.display = 'block';
        statusEl.textContent   = 'Converting 0 / ' + files.length + '...';

        for (var i = 0; i < files.length; i++) {
            var file    = files[i];
            var origExt = (file.name.split('.').pop() || 'IMG').toUpperCase();
            statusEl.textContent = 'Converting ' + (i + 1) + ' / ' + files.length + ': ' + file.name;
            try {
                var blob     = await window._convertFile(file, fmt.mimeType, fmt.quality);
                var base     = file.name.replace(/\\.[^.]+$/, '');
                var outName  = base + '.' + fmt.ext;
                var thumbUrl = URL.createObjectURL(blob);
                _converter.results.push({ name: outName, blob: blob, thumbUrl: thumbUrl });

                var card = document.createElement('div');
                card.style.cssText = 'background:rgba(0,0,0,0.3);border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.1);text-align:center;';
                card.innerHTML =
                    '<img src="' + thumbUrl + '" style="width:100%;height:100px;object-fit:cover;display:block;">' +
                    '<div style="padding:6px 6px 2px;font-size:10px;color:var(--brand-text-sec);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + outName + '">' + outName + '</div>' +
                    '<div style="padding:2px 6px 6px;display:flex;justify-content:center;gap:4px;align-items:center;">' +
                    '<span style="font-size:9px;background:rgba(255,255,255,0.15);padding:2px 5px;border-radius:3px;color:var(--brand-text-sec);">' + origExt + '</span>' +
                    '<span style="font-size:9px;color:var(--brand-text-sec);">&#x2192;</span>' +
                    '<span style="font-size:9px;background:var(--brand-primary);padding:2px 5px;border-radius:3px;color:#fff;font-weight:bold;">' + fmt.label + '</span>' +
                    '</div>';
                gridEl.appendChild(card);
            } catch(err) {
                console.error('Converter error for', file.name, err);
                var errCard = document.createElement('div');
                errCard.style.cssText = 'background:rgba(255,71,87,0.15);border-radius:6px;padding:10px;border:1px solid rgba(255,71,87,0.3);text-align:center;';
                errCard.innerHTML = '<div style="font-size:10px;color:var(--danger-red);">\u2717 ' + file.name + '<br>Failed</div>';
                gridEl.appendChild(errCard);
            }
        }

        statusEl.textContent = 'Done! ' + _converter.results.length + ' file(s) converted.';
        var ctrlEl = document.getElementById('converter-controls');
        var dlBtn  = document.getElementById('converter-download-btn');
        if (_converter.results.length > 0) {
            ctrlEl.style.display = 'block';
            dlBtn.innerText = _converter.results.length === 1
                ? '\u2B07 DOWNLOAD ' + fmt.label
                : '\u2B07 DOWNLOAD ' + _converter.results.length + ' FILES AS ZIP';
        }
    };

    window._convertFile = function(file, mimeType, quality) {
        return new Promise(function(resolve, reject) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var img = new Image();
                img.onload = function() {
                    var c    = document.createElement('canvas');
                    c.width  = img.naturalWidth  || img.width;
                    c.height = img.naturalHeight || img.height;
                    c.getContext('2d').drawImage(img, 0, 0);
                    c.toBlob(function(b) {
                        if (b) resolve(b); else reject(new Error('Export failed'));
                    }, mimeType, quality);
                };
                img.onerror = function() { reject(new Error('Failed to load image')); };
                img.src = e.target.result;
            };
            reader.onerror = function() { reject(new Error('Failed to read file')); };
            reader.readAsDataURL(file);
        });
    };

    window.downloadConverted = async function() {
        if (_converter.results.length === 0) return;
        var btn      = document.getElementById('converter-download-btn');
        var origText = btn.innerText;
        btn.disabled = true; btn.innerText = 'DOWNLOADING...';
        try {
            if (_converter.results.length === 1) {
                var r   = _converter.results[0];
                var url = URL.createObjectURL(r.blob);
                var a   = document.createElement('a');
                a.href = url; a.download = r.name;
                document.body.appendChild(a); a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } else {
                var zip = new JSZip();
                _converter.results.forEach(function(r) { zip.file(r.name, r.blob); });
                var zipBlob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 3 } });
                var url2 = URL.createObjectURL(zipBlob);
                var a2   = document.createElement('a');
                a2.href = url2; a2.download = 'converted-' + Date.now() + '.zip';
                document.body.appendChild(a2); a2.click();
                document.body.removeChild(a2);
                URL.revokeObjectURL(url2);
            }
            btn.innerText = 'DOWNLOADED! \u2713'; btn.style.background = 'var(--success-green)';
            setTimeout(function() { btn.innerText = origText; btn.style.background = ''; btn.disabled = false; }, 2500);
        } catch(err) {
            console.error(err);
            window.showAppAlert("Download Error", "Failed to download. Please try again.", "error");
            btn.innerText = origText; btn.disabled = false;
        }
    };
"""

# Insert before closing </script>
last_script_close = src.rfind('</script>')
src = src[:last_script_close] + NEW_JS + '\n</script>' + src[last_script_close + 9:]
print('4. Added new JS functions (download, batch, converter)')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 – WRAP IN HTML DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

# Pull head-level tags out of body content
TAB_CSS = """    <style>
    /* ── TOOL TABS ── */
    .tool-tab-bar {
        display: flex;
        border-bottom: 2px solid rgba(255,255,255,0.12);
        margin-bottom: 28px;
        gap: 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    .tool-tab-btn {
        background: none;
        border: none;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        padding: 11px 20px;
        color: var(--brand-text-sec);
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        transition: color 0.15s, border-color 0.15s;
        white-space: nowrap;
        font-family: 'Rubik', sans-serif;
    }
    .tool-tab-btn:hover { color: var(--brand-text-pri); }
    .tool-tab-btn.active { color: var(--brand-hover); border-bottom-color: var(--brand-hover); }
    .tool-tab-panel { display: none; }
    .tool-tab-panel.active { display: block; }
    </style>"""

HEAD_EXTRAS = (
    '    <script src="https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.4.3/dist/browser/umd/index.min.js"></script>\n'
    '    <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Cinzel:wght@400;700&family=Dancing+Script:wght@400;700&family=Oswald:wght@400;700&family=Pacifico&family=Permanent+Marker&family=Press+Start+2P&family=Roboto:wght@400;500;600;700&family=Shadows+Into+Light&display=swap" rel="stylesheet">\n'
    '    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>\n'
    '    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>\n'
    + TAB_CSS
)

src = src.replace('<script src="https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.4.3/dist/browser/umd/index.min.js"></script>\n', '')
src = src.replace('<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Cinzel:wght@400;700&family=Dancing+Script:wght@400;700&family=Oswald:wght@400;700&family=Pacifico&family=Permanent+Marker&family=Press+Start+2P&family=Roboto:wght@400;500;600;700&family=Shadows+Into+Light&display=swap" rel="stylesheet">\n', '')
src = src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>\n', '')

HTML = (
    '<!DOCTYPE html>\n'
    '<html lang="en">\n'
    '<head>\n'
    '    <meta charset="UTF-8">\n'
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '    <title>Playmat Studio</title>\n'
    + HEAD_EXTRAS + '\n'
    '</head>\n'
    '<body style="margin:0; padding:0; background:#0d0d0d; min-height:100vh;">\n'
    + src.strip() + '\n'
    '</body>\n'
    '</html>\n'
)

print('5. Wrapped in HTML document')

# ══════════════════════════════════════════════════════════════════════════════
# WRITE OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
os.makedirs(os.path.dirname(DEST), exist_ok=True)
with open(DEST, 'w', encoding='utf-8') as f:
    f.write(HTML)

size_kb = os.path.getsize(DEST) // 1024
print(f'\nDone! -> {DEST}')
print(f'File size: {size_kb} KB')
