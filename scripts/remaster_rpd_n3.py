from __future__ import annotations

import asyncio, hashlib, json, re, shutil
from pathlib import Path
import edge_tts
from pydub import AudioSegment, effects

ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'roteiros/RPD1-frozen.txt';OUT=ROOT/'audio';TMP=ROOT/'.tmp_rpd_n3'
VOICE='pt-BR-AntonioNeural';VERSION='n3-20260831';TARGET=-18.0
SOFT={'mas','porém','porem','contudo','entretanto','porque','quando','enquanto','então','entao','assim','agora','portanto','se','como','além','alem','ainda','depois','antes','embora'}
INSTR=('observe','imagine','pense','perceba','note','considere','guarde','faça','faca','tente')
REFL=('talvez','por enquanto','agora','às vezes','as vezes','vale lembrar','repare','uma possibilidade','isso pode')
CONC=('em resumo','para concluir','por fim','em síntese','em sintese','o ponto principal')

def norm(t):return re.sub(r'\s+',' ',t or '').strip()
def tok(t):return re.findall(r'[\wÀ-ÿ]+',t.lower(),flags=re.UNICODE)
def stable(t,lo,hi,s):
 h=hashlib.sha256((s+'|'+norm(t)).encode()).digest();u=int.from_bytes(h[:4],'big')/0xffffffff;return lo+int(round(u*(hi-lo)))
def intent(t):
 x=norm(t);l=x.lower()
 if x.endswith('?'):return 'question'
 if l.startswith(INSTR):return 'instruction'
 if l.startswith(REFL):return 'reflective'
 if l.startswith(CONC):return 'conclusion'
 if x.endswith('!'):return 'emphasis'
 return 'explain'
def units(text):
 text=norm(text);out=[]
 for sent in [s.strip() for s in re.split(r'(?<=[.!?…])\s+',text) if s.strip()]:
  w=sent.split()
  if len(w)<=20:out.append(sent);continue
  start=0
  while len(w)-start>20:
   lo=start+9;hi=min(start+20,len(w));target=min(start+14,hi);cand=[]
   for i in range(lo,hi):
    ww=re.sub(r'^[^\wÀ-ÿ]+|[^\wÀ-ÿ]+$','',w[i].lower())
    if ww in SOFT:cand.append(i)
   cut=min(cand,key=lambda i:abs(i-target)) if cand else target;u=' '.join(w[start:cut]).strip()
   if u and not u.endswith((',', ';', ':', '.', '?', '!', '…')):u+=','
   out.append(u);start=cut
  if start<len(w):out.append(' '.join(w[start:]).strip())
 if tok(' '.join(out))!=tok(text):raise RuntimeError('Gate lexical N3 falhou')
 return out
def prosody(text):
 i=intent(text);rate=-4+{'explain':0,'question':1,'instruction':-3,'reflective':-3,'conclusion':-2,'emphasis':1}[i];pitch=-1+{'explain':0,'question':2,'instruction':-1,'reflective':-1,'conclusion':-1,'emphasis':1}[i]
 rate+=stable(text,-1,1,'rate');pitch+=stable(text,-1,1,'pitch');ranges={'explain':(390,650),'question':(480,760),'instruction':(760,1250),'reflective':(720,1200),'conclusion':(650,1050),'emphasis':(390,650)};lo,hi=ranges[i]
 return i,f'{max(-12,min(4,rate)):+d}%',f'{max(-5,min(5,pitch)):+d}Hz',stable(text,lo,hi,'pause')
def frozen_text():
 lines=[]
 for line in SOURCE.read_text(encoding='utf-8').splitlines():
  if line.strip() and not line.lstrip().startswith('#'):lines.append(line.strip())
 text=norm(' '.join(lines))
 if not text:raise RuntimeError('Transcrição congelada vazia')
 return text
async def synth(text,rate,pitch,path,sem):
 async with sem:
  for attempt in range(1,4):
   try:
    c=edge_tts.Communicate(text=text,voice=VOICE,rate=rate,pitch=pitch,volume='+0%');await asyncio.wait_for(c.save(str(path)),timeout=55);return
   except Exception:
    if attempt==3:raise
    await asyncio.sleep(.9*attempt)
async def main():
 text=frozen_text();turns=units(text);OUT.mkdir(exist_ok=True);TMP.mkdir(exist_ok=True);sem=asyncio.Semaphore(4);tasks=[];seq=[];intents=[]
 for i,turn in enumerate(turns):
  it,rate,pitch,pause=prosody(turn);part=TMP/f'{i:03d}.mp3';seq.append((part,0 if i==len(turns)-1 else pause));tasks.append(synth(turn,rate,pitch,part,sem));intents.append(it)
 await asyncio.gather(*tasks);a=AudioSegment.silent(duration=150)
 for part,pause in seq:
  a+=AudioSegment.from_file(part,format='mp3')
  if pause:a+=AudioSegment.silent(duration=pause)
 a+=AudioSegment.silent(duration=280);a=effects.compress_dynamic_range(a,threshold=-20.0,ratio=2.0,attack=8.0,release=70.0)
 if a.dBFS!=float('-inf'):a=a.apply_gain(TARGET-a.dBFS)
 if a.max_dBFS>-1.2:a=a.apply_gain(-1.2-a.max_dBFS)
 target=OUT/'rpd1-n3.mp3';a.export(target,format='mp3',bitrate='128k',parameters=['-ac','1','-ar','44100'])
 spec={'version':VERSION,'voice':VOICE,'profile':'N3-C Natural — RPD','source':'roteiros/RPD1-frozen.txt','text_integrity':1.0,'ambient_audio':False,'prosody':'semantic-intent + respiratory-units + deterministic-content-jitter','intents':sorted(set(intents)),'turns':len(turns),'target_dbfs':TARGET,'peak_ceiling_dbfs':-1.2,'format':'MP3 128 kbps, mono, 44.1 kHz','duration_seconds':round(len(a)/1000,1)}
 (OUT/'audio-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');shutil.rmtree(TMP,ignore_errors=True);print(f'RPD N3 gerado: {spec["duration_seconds"]}s')
if __name__=='__main__':asyncio.run(main())
