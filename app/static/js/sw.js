/**
 * Service Worker para Push Notifications
 * PDV-MF Sistema de Caixa
 * ES5 Compativel
 * Versao: 1.0.1 - 09/01/2026
 */

var CACHE_NAME = 'pdv-mf-v1.0.1';
var urlsToCache = [
    '/',
    '/gerente',
    '/static/css/style.css',
    '/static/js/api.js',
    '/static/js/utils.js'
];

// Instalacao do Service Worker
self.addEventListener('install', function(event) {
    console.log('[SW] Instalando Service Worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('[SW] Cache aberto');
                return cache.addAll(urlsToCache);
            })
            .catch(function(err) {
                console.log('[SW] Erro ao abrir cache:', err);
            })
    );
    
    self.skipWaiting();
});

// Ativacao
self.addEventListener('activate', function(event) {
    console.log('[SW] Service Worker ativado');
    
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    return self.clients.claim();
});

// Receber notificacao push
self.addEventListener('push', function(event) {
    console.log('[SW] Push recebido:', event);
    
    var data = {
        title: 'PDV-MF',
        body: 'Nova notificacao',
        icon: '/static/img/icon-192.png',
        badge: '/static/img/badge-72.png',
        vibrate: [200, 100, 200],
        data: {},
        tag: 'geral',
        requireInteraction: true
    };
    
    if (event.data) {
        try {
            var payload = event.data.json();
            // Merge objects manually for ES5
            for (var key in payload) {
                if (payload.hasOwnProperty(key)) {
                    data[key] = payload[key];
                }
            }
        } catch (e) {
            data.body = event.data.text();
        }
    }
    
    var options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        vibrate: data.vibrate,
        data: data.data,
        tag: data.tag,
        requireInteraction: data.requireInteraction,
        actions: getActionsForType(data.data ? data.data.tipo : null)
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Acoes baseadas no tipo de notificacao
function getActionsForType(tipo) {
    if (tipo === 'sangria') {
        return [
            { action: 'ver', title: 'Ver Detalhes' },
            { action: 'fechar', title: 'Fechar' }
        ];
    } else if (tipo === 'abertura' || tipo === 'fechamento') {
        return [
            { action: 'painel', title: 'Abrir Painel' },
            { action: 'fechar', title: 'Fechar' }
        ];
    } else if (tipo === 'resumo_diario') {
        return [
            { action: 'pdf', title: 'Baixar PDF' },
            { action: 'painel', title: 'Ver Detalhes' }
        ];
    } else {
        return [
            { action: 'ver', title: 'Ver' },
            { action: 'fechar', title: 'Fechar' }
        ];
    }
}

// Clique na notificacao
self.addEventListener('notificationclick', function(event) {
    console.log('[SW] Notificacao clicada:', event);
    
    event.notification.close();
    
    var action = event.action;
    var data = event.notification.data || {};
    
    var url = '/gerente';
    
    if (action === 'pdf') {
        var hoje = new Date().toISOString().split('T')[0];
        url = '/api/relatorio/resumo-diario/pdf?data=' + hoje;
    } else if (action === 'painel') {
        url = '/gerente';
    } else if (action === 'ver') {
        url = '/gerente';
    } else if (action === 'fechar') {
        return;
    }
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(windowClients) {
                // Verificar se ja existe uma janela aberta
                for (var i = 0; i < windowClients.length; i++) {
                    var client = windowClients[i];
                    if (client.url.indexOf('/gerente') !== -1 && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Se nao, abrir nova janela
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// Fechar notificacao
self.addEventListener('notificationclose', function(event) {
    console.log('[SW] Notificacao fechada:', event);
});

// Fetch com cache fallback
self.addEventListener('fetch', function(event) {
    // Nao cachear requisicoes de API
    if (event.request.url.indexOf('/api/') !== -1) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
            .catch(function() {
                // Offline fallback
                if (event.request.mode === 'navigate') {
                    return caches.match('/');
                }
            })
    );
});
