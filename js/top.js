/* オーガキングダム トップページ（タブ・話数の範囲と並べ替え・コミックスの並べ替え） */
const tabs=[...document.querySelectorAll('.jp-tab')],
      panels=[...document.querySelectorAll('.jp-panel')];

function openTab(name, updateHash=true){
  tabs.forEach(x=>x.classList.remove('active'));
  panels.forEach(x=>x.classList.remove('active'));
  const btn=tabs.find(x=>x.dataset.tab===name);
  const panel=document.getElementById(name);
  if(btn&&panel){btn.classList.add('active');panel.classList.add('active');}
  if(updateHash){
    if(name==='comics') history.replaceState(null,'','#comics');
    else if(name==='info') history.replaceState(null,'','#info');
    else history.replaceState(null,'',location.pathname);
  }
}
tabs.forEach(btn=>btn.onclick=()=>openTab(btn.dataset.tab,true));

/* ---------- 話：1話から / 最新話から ---------- */
const episodePanel=document.getElementById('episodes');
const episodeList=episodePanel.querySelector('.episode-row').parentElement;
const rows=[...episodePanel.querySelectorAll('.episode-row')];
const rangeBar=episodePanel.querySelector('.range-bar');
const rangeButtons=[...rangeBar.querySelectorAll('.range-btn')];
const episodeSortButtons=[...episodePanel.querySelectorAll('.episode-sort .sort-btn')];

function showRange(key){
  const [a,b]=key.split('-').map(Number);
  rows.forEach(r=>{
    const n=+r.dataset.ep;
    r.style.display=(n>=a&&n<=b)?'grid':'none';
  });
}

function activateRange(btn){
  rangeButtons.forEach(x=>x.classList.remove('active'));
  btn.classList.add('active');
  showRange(btn.dataset.range);
}

rangeButtons.forEach(btn=>btn.onclick=()=>activateRange(btn));

function setEpisodeOrder(order){
  episodeSortButtons.forEach(b=>b.classList.toggle('active',b.dataset.order===order));

  const sortedRows=[...rows].sort((a,b)=>{
    const av=+a.dataset.ep, bv=+b.dataset.ep;
    return order==='asc' ? av-bv : bv-av;
  });
  sortedRows.forEach(r=>episodeList.appendChild(r));

  const sortedRanges=[...rangeButtons].sort((a,b)=>{
    const av=+a.dataset.range.split('-')[0], bv=+b.dataset.range.split('-')[0];
    return order==='asc' ? av-bv : bv-av;
  });
  sortedRanges.forEach(b=>rangeBar.appendChild(b));

  const target = order==='asc'
    ? rangeButtons.reduce((m,b)=>+b.dataset.range.split('-')[0] < +m.dataset.range.split('-')[0] ? b : m)
    : rangeButtons.reduce((m,b)=>+b.dataset.range.split('-')[0] > +m.dataset.range.split('-')[0] ? b : m);
  activateRange(target);
}

episodeSortButtons.forEach(btn=>btn.onclick=()=>setEpisodeOrder(btn.dataset.order));
setEpisodeOrder('asc');

/* ---------- コミックス：1巻から / 最新巻から ---------- */
const comicsPanel=document.getElementById('comics');
const volumeList=comicsPanel.querySelector('.volume-list');
const volumes=[...volumeList.querySelectorAll('.volume-tile')];
const comicSortButtons=[...comicsPanel.querySelectorAll('.comics-sort .sort-btn')];

volumes.forEach((v,i)=>v.dataset.volume=i+1);

function setComicOrder(order){
  comicSortButtons.forEach(b=>b.classList.toggle('active',b.dataset.order===order));
  [...volumes]
    .sort((a,b)=>{
      const av=+a.dataset.volume, bv=+b.dataset.volume;
      return order==='asc' ? av-bv : bv-av;
    })
    .forEach(v=>volumeList.appendChild(v));
}
comicSortButtons.forEach(btn=>btn.onclick=()=>setComicOrder(btn.dataset.order));
setComicOrder('asc');

if(location.hash==='#comics') openTab('comics',false);
else if(location.hash==='#info') openTab('info',false);
else openTab('episodes',false);
