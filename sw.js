const CACHE = 'foodlist-v8';

let PHOTOS = [];
try {
	importScripts('./pics/list.js');
	PHOTOS = (self.FOOD_PICS || []).map((p) => './' + p);
} catch (err) {
	PHOTOS = [];
}

const ASSETS = [
	'./',
	'./index.html',
	'./manifest.webmanifest',
	'./pics/list.js',
	'./icons/icon-180.png',
	'./icons/icon-192.png',
	'./icons/icon-512.png'
].concat(PHOTOS);

self.addEventListener('install', (e) => {
	e.waitUntil(
		caches.open(CACHE)
			.then((c) => c.addAll(ASSETS))
			.then(() => self.skipWaiting())
	);
});

self.addEventListener('activate', (e) => {
	e.waitUntil(
		caches.keys()
			.then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
			.then(() => self.clients.claim())
	);
});

self.addEventListener('fetch', (e) => {
	const req = e.request;
	if (req.method !== 'GET') return;
	if (new URL(req.url).origin !== location.origin) return;

	const cacheFirst = (req) => caches.match(req).then((hit) => hit || fetch(req));

	const offline = () =>
		caches.match('./index.html').then((hit) => hit || caches.match('./'));

	// 断网/被墙时 fetch 可能挂很久，2.5 秒拿不到就直接用缓存
	const withTimeout = (promise, ms) =>
		Promise.race([
			promise,
			new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms))
		]);

	// 页面导航走网络优先：改了 index.html 立刻生效；网络不通时快速回落缓存
	if (req.mode === 'navigate') {
		e.respondWith(
			withTimeout(fetch(req), 2500)
				.then((res) => {
					if (!res || !res.ok) return offline();
					const copy = res.clone();
					caches.open(CACHE).then((c) => c.put('./index.html', copy));
					return res;
				})
				.catch(offline)
		);
		return;
	}

	e.respondWith(cacheFirst(req));
});
