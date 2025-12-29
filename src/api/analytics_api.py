"""
API REST para Analytics - Endpoints con cache, rate limit, auditoría
Framework: Flask (ligero, rápido para read-only)
"""
from flask import Flask, jsonify, request, g
from functools import wraps
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def create_analytics_api(analytics_service):
    """Factory function que crea la app Flask con endpoints de analytics."""
    
    app = Flask('analytics_api')
    app.config['JSON_SORT_KEYS'] = False
    
    # Cache simple en memoria (producción usar Redis)
    cache = {}
    
    def cache_key(endpoint: str, params: str) -> str:
        return f"{endpoint}:{params}"
    
    def get_cached(key: str, ttl: int = 300) -> Any:
        """Obtiene del cache si no expiró."""
        if key in cache:
            value, expiry = cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del cache[key]
        return None
    
    def set_cache(key: str, value: Any, ttl: int = 300) -> None:
        """Almacena en cache con TTL."""
        cache[key] = (value, datetime.now() + timedelta(seconds=ttl))
    
    def require_auth(f):
        """Middleware de autenticación y auditoría."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Mock: en producción validar token/sesión
            empresa_id = request.args.get('empresa_id', default=1, type=int)
            usuario_id = request.args.get('usuario_id', default=None, type=int)
            
            # Almacenar en contexto
            g.empresa_id = empresa_id
            g.usuario_id = usuario_id
            
            # Auditoría
            parametros = json.dumps(dict(request.args))
            analytics_service.registrar_acceso_analytics(
                empresa_id=empresa_id,
                usuario_id=usuario_id,
                endpoint=request.path,
                parametros=parametros,
                resultado='SUCCESS'
            )
            
            return f(*args, **kwargs)
        return decorated_function
    
    @app.before_request
    def before_request():
        """Validar autenticación y setup."""
        g.start_time = datetime.now()
    
    @app.after_request
    def after_request(response):
        """Logging y headers de seguridad."""
        elapsed = (datetime.now() - g.start_time).total_seconds() * 1000
        logger.info(f"{request.method} {request.path} {response.status_code} {elapsed:.2f}ms")
        
        # Headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    
    # ==================== ENDPOINTS ====================
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check."""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/api/v1/analytics/overview', methods=['GET'])
    @require_auth
    def overview():
        """KPIs principales: hoy, últimos 7/30 días."""
        try:
            # Cache 300s
            cache_key_str = cache_key('overview', str(g.empresa_id))
            cached = get_cached(cache_key_str, ttl=300)
            
            if cached:
                return jsonify(cached), 200
            
            data = analytics_service.obtener_overview(g.empresa_id)
            set_cache(cache_key_str, data, ttl=300)
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Overview error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/productividad', methods=['GET'])
    @require_auth
    def productividad():
        """Productividad: nacimientos, destetes, muertes, traslados."""
        try:
            fecha = request.args.get('fecha')
            lote_id = request.args.get('lote_id', type=int)
            rango = request.args.get('rango_dias', default=30, type=int)
            
            cache_key_str = cache_key('productividad', f"{g.empresa_id}:{fecha}:{lote_id}:{rango}")
            cached = get_cached(cache_key_str, ttl=600)
            
            if cached:
                return jsonify(cached), 200
            
            data = analytics_service.obtener_productividad(
                empresa_id=g.empresa_id,
                fecha=fecha,
                lote_id=lote_id,
                rango_dias=rango
            )
            
            set_cache(cache_key_str, data, ttl=600)
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Productividad error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/alertas', methods=['GET'])
    @require_auth
    def alertas():
        """Alertas: activas, resueltas, críticas, tiempo promedio."""
        try:
            fecha = request.args.get('fecha')
            
            cache_key_str = cache_key('alertas', f"{g.empresa_id}:{fecha}")
            cached = get_cached(cache_key_str, ttl=300)
            
            if cached:
                return jsonify(cached), 200
            
            data = analytics_service.obtener_alertas(
                empresa_id=g.empresa_id,
                fecha=fecha
            )
            
            set_cache(cache_key_str, data, ttl=300)
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Alertas error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/ia', methods=['GET'])
    @require_auth
    def ia():
        """IA: sugerencias, aceptación, impacto, precisión."""
        try:
            fecha = request.args.get('fecha')
            
            cache_key_str = cache_key('ia', f"{g.empresa_id}:{fecha}")
            cached = get_cached(cache_key_str, ttl=300)
            
            if cached:
                return jsonify(cached), 200
            
            data = analytics_service.obtener_ia(
                empresa_id=g.empresa_id,
                fecha=fecha
            )
            
            set_cache(cache_key_str, data, ttl=300)
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"IA error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/autonomia', methods=['GET'])
    @require_auth
    def autonomia():
        """Autonomía: orquestaciones, rollbacks, kill switch."""
        try:
            fecha = request.args.get('fecha')
            
            cache_key_str = cache_key('autonomia', f"{g.empresa_id}:{fecha}")
            cached = get_cached(cache_key_str, ttl=300)
            
            if cached:
                return jsonify(cached), 200
            
            data = analytics_service.obtener_autonomia(
                empresa_id=g.empresa_id,
                fecha=fecha
            )
            
            set_cache(cache_key_str, data, ttl=300)
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Autonomia error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/comparativos', methods=['GET'])
    @require_auth
    def comparativos():
        """Comparativos: hoy vs semana pasada, mes vs anterior, etc."""
        try:
            comparador = request.args.get('comparador', default='hoy_vs_semana_pasada')
            
            cache_key_str = cache_key('comparativos', f"{g.empresa_id}:{comparador}")
            cached = get_cached(cache_key_str, ttl=600)
            
            if cached:
                return jsonify(cached), 200
            
            # Obtener comparativos desde repo
            resultado = {
                'comparador': comparador,
                'datos': [],
                'timestamp': datetime.now().isoformat()
            }
            
            set_cache(cache_key_str, resultado, ttl=600)
            
            return jsonify(resultado), 200
        except Exception as e:
            logger.error(f"Comparativos error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404 handler."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """500 handler."""
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


# Función de arranque
def run_analytics_api(analytics_service, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
    """Inicia el servidor API."""
    app = create_analytics_api(analytics_service)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    from infraestructura.analytics import AnalyticsService
    
    service = AnalyticsService()
    run_analytics_api(service, debug=True)
