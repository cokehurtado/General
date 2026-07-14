"""Capa de ingesta de The Cote.

Automatiza la entrada de datos al motor, con dos vías (ver README):
  - Automática y legal: fuentes limpias vía adapter (subastas públicas, APIs).
  - Semi-automática sin riesgo: extractor 'pega-el-texto' (tú traes el deal).

Los sitios protegidos (Chrono24/WatchCharts) viven como stubs deshabilitados
detrás de un 'gate legal' — ver sources/protected.py.

Distinción de diseño:
  - record_type 'sale'  = precio de cierre (subasta/eBay sold) → calibra fair value.
  - record_type 'offer' = anuncio activo comprable → se escanea como arbitraje.
"""
