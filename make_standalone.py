"""
Convert index_individual.html to fully standalone (no external file deps).
- Standard libs → CDN
- Custom/small libs → inline
- Unused libs → removed
"""
import os

BASE = 'C:/Users/Administrator/gaza_vaccination'

def read_local(path):
    full = os.path.join(BASE, path)
    if os.path.exists(full):
        with open(full, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    return f'/* {path} NOT FOUND */'

with open(os.path.join(BASE, 'index_individual.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# ── CSS replacements ──────────────────────────────────────────────────────────
css_replacements = {
    '<link rel="stylesheet" href="css/leaflet.css">':
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">',

    '<link rel="stylesheet" href="css/L.Control.Layers.Tree.css">':
        '',  # not used

    '<link rel="stylesheet" href="css/L.Control.Locate.min.css">':
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.79.0/dist/L.Control.Locate.min.css">',

    '<link rel="stylesheet" href="css/qgis2web.css">':
        '<style>\n' + read_local('css/qgis2web.css') + '\n</style>',

    '<link rel="stylesheet" href="css/fontawesome-all.min.css">':
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',

    '<link rel="stylesheet" href="css/leaflet-search.css">':
        '<style>\n' + read_local('css/leaflet-search.css') + '\n</style>',

    '<link rel="stylesheet" href="css/nouislider.min.css">':
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.1/nouislider.min.css">',

    '<link rel="stylesheet" href="css/leaflet.photon.css">':
        '<style>\n' + read_local('css/leaflet.photon.css') + '\n</style>',

    '<link rel="stylesheet" href="css/leaflet-measure.css">':
        '<style>\n' + read_local('css/leaflet-measure.css') + '\n</style>',
}

# ── JS replacements ───────────────────────────────────────────────────────────
js_replacements = {
    '<script src="js/qgis2web_expressions.js"></script>':
        '<script>\n' + read_local('js/qgis2web_expressions.js') + '\n</script>',

    '<script src="js/leaflet.js"></script>':
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',

    '<script src="js/L.Control.Layers.Tree.min.js"></script>':
        '',  # not used

    '<script src="js/L.Control.Locate.min.js"></script>':
        '<script src="https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.79.0/dist/L.Control.Locate.min.js"></script>',

    '<script src="js/leaflet.rotatedMarker.js"></script>':
        '',  # not used (circle markers)

    '<script src="js/leaflet.pattern.js"></script>':
        '<script>\n' + read_local('js/leaflet.pattern.js') + '\n</script>',

    '<script src="js/leaflet-hash.js"></script>':
        '<script>\n' + read_local('js/leaflet-hash.js') + '\n</script>',

    '<script src="js/Autolinker.min.js"></script>':
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/autolinker/3.14.4/Autolinker.min.js"></script>',

    '<script src="js/rbush.min.js"></script>':
        '<script>\n' + read_local('js/rbush.min.js') + '\n</script>',

    '<script src="js/labelgun.min.js"></script>':
        '<script>\n' + read_local('js/labelgun.min.js') + '\n</script>',

    '<script src="js/labels.js"></script>':
        '<script>\n' + read_local('js/labels.js') + '\n</script>',

    '<script src="js/leaflet.photon.js"></script>':
        '<script>\n' + read_local('js/leaflet.photon.js') + '\n</script>',

    '<script src="js/leaflet-measure.js"></script>':
        '<script>\n' + read_local('js/leaflet-measure.js') + '\n</script>',

    '<script src="js/leaflet-search.js"></script>':
        '<script>\n' + read_local('js/leaflet-search.js') + '\n</script>',

    '<script src="js/nouislider.min.js"></script>':
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.1/nouislider.min.js"></script>',

    '<script src="js/wNumb.js"></script>':
        '<script>\n' + read_local('js/wNumb.js') + '\n</script>',
}

for old, new in {**css_replacements, **js_replacements}.items():
    if old in html:
        html = html.replace(old, new)
        print(f'✓ replaced: {old[:60]}')
    else:
        print(f'✗ NOT FOUND: {old[:60]}')

out_path = os.path.join(BASE, 'index_individual.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out_path) // 1024
print(f'\nDone → {out_path}')
print(f'Final size: {size_kb} KB')
