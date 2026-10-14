const $=s=>document.querySelector(s);let rows=[],key='usd',dir=-1;
// Parse a dollar amount only if the stated value contains "$<number>"; "/month" amounts are annualized ×12 for ranking and labeled.
function usd(v){const m=String(v).match(/\$\s?([\d,]+(?:\.\d+)?)/);if(!m)return null;let n=parseFloat(m[1].replace(/,/g,''));
  const per=/\/\s?mo|month/i.test(v);return {n:per?n*12:n,per};}
const cardRank={no:0,'not stated':1,yes:2};
fetch('/data/offers.json').then(r=>r.json()).then(o=>{rows=o.map(x=>({...x,u:usd(x.value)}));
  [...new Set(o.map(x=>x.category))].sort().forEach(c=>$('#cat').insertAdjacentHTML('beforeend',`<option>${c}</option>`));
  rows.sort((a,b)=>(b.u?.n??-1)-(a.u?.n??-1)||(cardRank[a.card_required]??1)-(cardRank[b.card_required]??1)).forEach((x,i)=>x.rank=i+1);render();});
function val(x,k){return k=='usd'?(x.u?.n??-1):k=='card'?(cardRank[x.card_required]??1):k=='rank'?x.rank:String(x[k]||'').toLowerCase();}
function render(){const q=$('#q').value.toLowerCase(),c=$('#cat').value;
  const r=rows.filter(x=>(!c||x.category==c)&&(x.name+x.provider+x.offer+x.category).toLowerCase().includes(q))
    .sort((a,b)=>{const A=val(a,key),B=val(b,key);return (A>B?1:A<B?-1:0)*dir||a.rank-b.rank;});
  $('#count').textContent=r.length+' offers';
  $('#rows').innerHTML=r.map(x=>`<tr><td>${x.rank}</td><td><b>${x.name}</b><br><small class="muted">${x.provider}</small></td><td><span class="tag">${x.category}</span><br><small>${x.offer}</small></td>
  <td>${x.u?('$'+x.u.n.toLocaleString()+(x.u.per?' <small class="muted">/yr (from monthly)</small>':'')):'<small class="muted">not comparable in $</small>'}</td>
  <td>${x.value}</td><td class="${x.card_required=='no'?'no':''}">${x.card_required}</td><td>${x.resets}</td><td><a href="${x.source_url}" target="_blank" rel="noopener">official page ↗</a><br><small class="muted">checked ${x.last_checked}</small></td></tr>`).join('');}
document.querySelectorAll('th.sort').forEach(th=>th.addEventListener('click',()=>{const k=th.dataset.k;dir=(k==key)?-dir:(k=='usd'?-1:1);key=k;
  document.querySelectorAll('th.sort').forEach(t=>t.textContent=t.textContent.replace(/ [▲▼]$/,''));th.textContent+=dir>0?' ▲':' ▼';render();}));
['#q','#cat'].forEach(s=>$(s).addEventListener('input',render));
