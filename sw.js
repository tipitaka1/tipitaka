/* 껍데기(index.html)는 새것을 먼저 받아 본다 — 앱을 고쳤을 때 바로 반영되도록.
   자료(data.bin)와 아이콘은 캐시를 먼저 쓴다 — 2.8MB 를 매번 받지 않도록. */
const C='kyl3-pub-2026-08-28a';
const F=['./','./index.html','./data.bin','./f-kr.woff2','./f-krb.woff2','./f-pali.woff2',
         './manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{}));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});
const shell=u=> u.mode==='navigate' || /\/(index\.html)?$|\.html$|manifest\.webmanifest$/.test(new URL(u.url).pathname);
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const put=r=>{ const cp=r.clone(); caches.open(C).then(c=>c.put(e.request,cp)).catch(()=>{}); return r; };
  if(shell(e.request)){
    e.respondWith(fetch(e.request).then(put)
      .catch(()=>caches.match(e.request).then(r=>r||caches.match('./index.html'))));
  }else{
    e.respondWith(caches.match(e.request).then(r=> r || fetch(e.request).then(put)));
  }
});