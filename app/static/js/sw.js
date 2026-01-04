/**
 * Service Worker para Push Notifications
 * PDV-MF Sistema de Caixa
 */

const CACHE_NAME = 'pdv-mf-v1';
const urlsToCache = [
    '/',
    '/gerente',
    '/static/css/style.css',
    '/static/js/api.js',
    '/static/js/utils.js'
];

// Instalação do Service Worker
self.addEventListener('install', event => {
    console.log('[SW] Instalando Service Worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Cache aberto');
                return cache.addAll(urlsToCache);
            })
            .catch(err => {
                console.log('[SW] Erro ao abrir cache:', err);
            })
    );
    
    self.skipWaiting();
});

// Ativação
self.addEventListener('activate', event => {
    console.log('[SW] Service Worker ativado');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
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

// Receber notificação push
self.addEventListener('push', event => {
    console.log('[SW] Push recebido:', event);
    
    let data = {
        title: '🔔 PDV-MF',
        body: 'Nova notificação',
        icon: '/static/img/icon-192.png',
        badge: '/static/img/badge-72.png',
        vibrate: [200, 100, 200],
        data: {},
        tag: 'geral',
        requireInteraction: true
    };
    
    if (event.data) {
        try {
            const payload = event.data.json();
            data = { ...data, ...payload };
        } catch (e) {
            data.body = event.data.text();
        }
    }
    
    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        vibrate: data.vibrate,
        data: data.data,
        tag: data.tag,
        requireInteraction: data.requireInteraction,
        actions: getActionsForType(data.data?.tipo)
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Ações baseadas no tipo de notificação
function getActionsForType(tipo) {
    switch (tipo) {
        case 'sangria':
            return [
                { action: 'ver', title: '👁️ Ver Detalhes' },
                { action: 'fechar', title: '✖️ Fechar' }
            ];
        case 'abertura':
        case 'fechamento':
            return [
                { action: 'painel', title: '📊 Abrir Painel' },
                { action: 'fechar', title: '✖️ Fechar' }
            ];
        case 'resumo_diario':
            return [
                { action: 'pdf', title: '📄 Baixar PDF' },
                { action: 'painel', title: '📊 Ver Detalhes' }
            ];
        default:
            return [
                { action: 'ver', title: '👁️ Ver' },
                { action: 'fechar', title: '✖️ Fechar' }
            ];
    }
}

// Clique na notificação
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notificação clicada:', event);
    
    event.notification.close();
    
    const action = event.action;
    const data = event.notification.data || {};
    
    let url = '/gerente';
    
    if (action === 'pdf') {
        const hoje = new Date().toISOString().split('T')[0];
        url = `/api/relatorio/resumo-diario/pdf?data=${hoje}`;
    } else if (action === 'painel') {
        url = '/gerente';
    } else if (action === 'ver') {
        url = '/gerente';
    } else if (action === 'fechar') {
        return;
    }
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(windowClients => {
                // Verificar se já existe uma janela aberta
                for (let client of windowClients) {
                    if (client.url.includes('/gerente') && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Se não, abrir nova janela
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// Fechar notificação
self.addEventListener('notificationclose', event => {
    console.log('[SW] Notificação fechada:', event);
});

// Fetch com cache fallback
self.addEventListener('fetch', event => {
    // Não cachear requisições de API
    if (event.request.url.includes('/api/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
            .catch(() => {
                // Offline fallback
                if (event.request.mode === 'navigate') {
                    return caches.match('/');
                }
            })
    );
});
