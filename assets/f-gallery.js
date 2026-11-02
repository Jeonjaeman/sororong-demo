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
  function show(n){ li=(n+lbl.length)%lbl.length; lbi.src=lbl[li]; lbc.textContent=(li+1)+' / '+lbl.length; [li+1,li-1].forEach(function(k){ (new Image()).src=lbl[(k+lbl.length)%lbl.length]; }); }
  function close(){ lb.hidden=true; document.body.style.overflow=''; lbi.removeAttribute('src'); }
  grid.addEventListener('click',function(e){ var a=e.target.closest('a'); if(!a) return; e.preventDefault(); lbl=list.map(function(x){return src(x)}); lb.hidden=false; document.body.style.overflow='hidden'; show(+a.dataset.i); });
  lb.querySelector('.x').onclick=close; lb.querySelector('.pv').onclick=function(){show(li-1)}; lb.querySelector('.nx').onclick=function(){show(li+1)};
  lb.addEventListener('click',function(e){ if(e.target===lb) close(); });
  document.addEventListener('keydown',function(e){ if(lb.hidden) return; if(e.key==='Escape') close(); if(e.key==='ArrowLeft') show(li-1); if(e.key==='ArrowRight') show(li+1); });
  // 모바일 스와이프: 좌우로 넘기기, 아래로 내려 닫기
  var tx=0,ty=0,dx=0,dy=0,touching=false;
  lb.addEventListener('touchstart',function(e){ if(e.touches.length!==1) return; touching=true; tx=e.touches[0].clientX; ty=e.touches[0].clientY; dx=dy=0; lbi.style.transition='none'; },{passive:true});
  lb.addEventListener('touchmove',function(e){ if(!touching) return; dx=e.touches[0].clientX-tx; dy=e.touches[0].clientY-ty; if(Math.abs(dx)>Math.abs(dy)) lbi.style.transform='translateX('+dx+'px)'; else if(dy>0) lbi.style.transform='translateY('+dy+'px)'; e.preventDefault(); },{passive:false});
  lb.addEventListener('touchend',function(){ if(!touching) return; touching=false; lbi.style.transition='transform .25s ease';
    if(Math.abs(dx)>50 && Math.abs(dx)>Math.abs(dy)){ var d=dx<0?1:-1; lbi.style.transform='translateX('+(-d*window.innerWidth)+'px)'; setTimeout(function(){ lbi.style.transition='none'; show(li+d); lbi.style.transform='translateX('+(d*window.innerWidth*.4)+'px)'; requestAnimationFrame(function(){ requestAnimationFrame(function(){ lbi.style.transition='transform .25s ease'; lbi.style.transform=''; }); }); },180); }
    else if(dy>90 && dy>Math.abs(dx)){ lbi.style.transform=''; close(); }
    else lbi.style.transform=''; });
})();
