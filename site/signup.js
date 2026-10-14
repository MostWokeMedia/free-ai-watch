// Weekly digest signup: posts to /api/subscribe (Cloudflare Pages Function). No third-party trackers.
document.querySelectorAll('form.signup').forEach(f=>f.addEventListener('submit',async e=>{
  e.preventDefault();const msg=f.querySelector('.msg'),btn=f.querySelector('button');btn.disabled=true;msg.textContent='Saving…';
  try{const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email:f.email.value,website:f.website.value,source:location.pathname})});
    const j=await r.json().catch(()=>({}));
    msg.textContent=r.ok?'✅ You’re in — first weekly digest lands soon.':(j.error||'Sorry, signup is temporarily unavailable. Try again later.');
    if(r.ok)f.email.value='';}catch(_){msg.textContent='Network error — try again.';}
  btn.disabled=false;}));
