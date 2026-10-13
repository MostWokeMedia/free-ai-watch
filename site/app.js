const $=s=>document.querySelector(s);let offers=[],changes=[];
Promise.all([fetch('data/offers.json').then(r=>r.json()),fetch('data/changes.json').then(r=>r.json())]).then(([o,c])=>{offers=o;changes=c;
[...new Set(o.map(x=>x.category))].sort().forEach(c=>$('#cat').insertAdjacentHTML('beforeend',`<option>${c}</option>`));render();feed();soon();route();});
function render(){const q=$('#q').value.toLowerCase(),c=$('#cat').value,k=$('#card').value;
const r=offers.filter(x=>(!c||x.category==c)&&(!k||x.card_required==k)&&(x.name+x.provider+x.offer).toLowerCase().includes(q));
$('#count').textContent=r.length+' offers';$('#rows').innerHTML=r.map(x=>`<tr><td><a href="${x.source_url}" target="_blank" rel="noopener">${x.name}</a><span class="tag">${x.category}</span><br><small>${x.offer}</small></td><td>${x.provider}</td><td>${x.value}</td><td class="${x.card_required=='no'?'no':''}">${x.card_required}</td><td>${x.resets}</td><td>${x.deadline||'—'}</td><td>${x.last_checked}</td></tr>`).join('');}
function feed(){const d=changes[0]?.date;const t=changes.filter(x=>x.date==d);$('#feed').innerHTML=`<p>${t.length} change events on ${d}</p>`+t.map(x=>`<li><b>${x.type.replace('_',' ')}</b> — <a href="${x.source_url}" target="_blank">${x.name}</a>: <small>${x.detail}</small></li>`).join('');}
function soon(){const n=Date.now();const s=offers.filter(x=>x.deadline).sort((a,b)=>a.deadline.localeCompare(b.deadline));
$('#soon').innerHTML=s.length?s.map(x=>`<li><b>${Math.floor((new Date(x.deadline+'T23:59:59')-n)/864e5)} days left</b> — <a href="${x.source_url}" target="_blank">${x.name}</a> (${x.value}) · ends ${x.deadline}</li>`).join(''):'<li>No verified deadlines right now.</li>';}
function route(){const h=location.hash.slice(1)||'all';document.querySelectorAll('main section').forEach(s=>s.hidden=s.id!=h);document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.hash=='#'+h));}
addEventListener('hashchange',route);['#q','#cat','#card'].forEach(s=>$(s).addEventListener('input',render));
