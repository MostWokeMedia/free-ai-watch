// Generic JSON form poster for /submit and /sponsor. Shows server messages as text (never HTML).
document.querySelectorAll('form[data-endpoint]').forEach(f=>f.addEventListener('submit',async e=>{
  e.preventDefault();const msg=f.querySelector('.msg'),btn=f.querySelector('button[type=submit]');btn.disabled=true;msg.textContent='Sending…';
  const data=Object.fromEntries(new FormData(f));
  try{const r=await fetch(f.dataset.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    const j=await r.json().catch(()=>({}));msg.textContent=r.ok?(j.message||'Thanks, received.'):(j.error||'Something went wrong. Please try again later.');
    msg.className='msg '+(r.ok?'ok':'err');if(r.ok)f.reset();}catch(_){msg.textContent='Network error. Please try again.';msg.className='msg err';}
  btn.disabled=false;}));
