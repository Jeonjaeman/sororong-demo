// F안 메뉴별 페이지 갤러리 + 확대 보기
(function(){
  var el=document.getElementById('gdata'); if(!el) return;
  var G=JSON.parse(el.textContent), gl={biz:'기업 · 관공서',sch:'학교 · 유치원',fam:'돌잔치 · 개인',wrt:'벌룬화환',flw:'자이언트플라워',hel:'헬륨 · 레터링'};
  var grid=document.querySelector('[data-ggrid]'), more=document.querySelector('[data-gmore]'), gtabs=document.querySelectorAll('[data-gtabs] button');
  var cur='all', shown=0, STEP=window.innerWidth<640?18:24, list=G;
  function src(x,t){ var n=('00'+x[1]).slice(-3); return 'assets/real/'+x[0]+'/'+(t?'t/':'')+n+'.jpg'; }
  function render(reset){
    if(reset){ grid.innerHTML=''; shown=0; list=cur==='all'?G:G.filter(function(x){return x[0]===cur}); }
    var end=Math.min(list.length,shown+STEP), frag=document.createDocumentFragment();
    for(var k=shown;k<end;k++){ var a=document.createElement('a'); a.href=src(list[k]); a.dataset.i=k; a.innerHTML='<img src="'+src(list[k],1)+'" alt="'+gl[list[k][0]]+' 현장 사진" loading="lazy">'; frag.appendChild(a); }
    grid.appendChild(frag); shown=end;
    more.parentNode.style.display=shown>=list.length?'none':''; more.querySelector('span').textContent='('+shown+' / '+list.length+')';
  }
  gtabs.forEach(function(b){ b.addEventListener('click',function(){ gtabs.forEach(function(x){x.classList.remove('on')}); b.classList.add('on'); cur=b.dataset.g; render(true); }); });
  more.addEventListener('click',function(){render(false)});
  render(true);
  var lb=document.querySelector('[data-lbox]'), lbi=lb.querySelector('img'), lbc=lb.querySelector('.ct'), lbl=[], li=0;
  function show(n){ li=(n+lbl.length)%lbl.length; lbi.src=lbl[li]; lbc.textContent=(li+1)+' / '+lbl.length; }
  function close(){ lb.hidden=true; document.body.style.overflow=''; lbi.removeAttribute('src'); }
  grid.addEventListener('click',function(e){ var a=e.target.closest('a'); if(!a) return; e.preventDefault(); lbl=list.map(function(x){return src(x)}); lb.hidden=false; document.body.style.overflow='hidden'; show(+a.dataset.i); });
  lb.querySelector('.x').onclick=close; lb.querySelector('.pv').onclick=function(){show(li-1)}; lb.querySelector('.nx').onclick=function(){show(li+1)};
  lb.addEventListener('click',function(e){ if(e.target===lb) close(); });
  document.addEventListener('keydown',function(e){ if(lb.hidden) return; if(e.key==='Escape') close(); if(e.key==='ArrowLeft') show(li-1); if(e.key==='ArrowRight') show(li+1); });
})();
