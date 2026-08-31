(()=>{'use strict';
const KEY='rpd.audioProgress.n3';let active=null;
document.querySelectorAll('audio').forEach((audio,index)=>{
  audio.preload='metadata';const id=audio.dataset.audioId||`rpd-${index+1}`;
  try{const saved=JSON.parse(localStorage.getItem(KEY)||'{}');const t=Number(saved[id]||0);if(t>0)audio.addEventListener('loadedmetadata',()=>{if(t<audio.duration-2)audio.currentTime=t},{once:true})}catch(e){}
  audio.addEventListener('play',()=>{if(active&&active!==audio)active.pause();active=audio});
  audio.addEventListener('timeupdate',()=>{if(!Number.isFinite(audio.currentTime)||audio.currentTime<1)return;try{const saved=JSON.parse(localStorage.getItem(KEY)||'{}');saved[id]=Math.floor(audio.currentTime);localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}});
  audio.addEventListener('ended',()=>{try{const saved=JSON.parse(localStorage.getItem(KEY)||'{}');delete saved[id];localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}if(active===audio)active=null});
});
})();
