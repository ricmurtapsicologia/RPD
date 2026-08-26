from __future__ import annotations

import asyncio
import json
import re
import shutil
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel
from pydub import AudioSegment, effects

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'RPD1.mp3'
ROTEIROS=ROOT/'roteiros'
OUT=ROOT/'audio'
TMP=ROOT/'.tmp_rpd_n2'
VOICE='pt-BR-AntonioNeural'
VERSION='n2-20260825'
OPENING_SILENCE_MS=130
ENDING_SILENCE_MS=240
TARGET_DBFS=-18.0
MAX_TURN_CHARS=560


def norm(text:str)->str:
    return re.sub(r'\s+',' ',text or '').strip()


def transcribe()->list[str]:
    model=WhisperModel('small',device='cpu',compute_type='int8')
    segments,_=model.transcribe(str(SOURCE),language='pt',beam_size=5,vad_filter=True,condition_on_previous_text=True,temperature=0.0)
    rows=[]
    for seg in segments:
        t=norm(seg.text)
        if t: rows.append(t)
    if not rows: raise RuntimeError('Nenhuma fala reconhecida no RPD1.mp3')
    return rows


def build_turns(rows:list[str])->list[str]:
    turns=[];cur=''
    for row in rows:
        candidate=f'{cur} {row}'.strip()
        if cur and len(candidate)>MAX_TURN_CHARS:
            turns.append(cur);cur=row
        else: cur=candidate
    if cur:turns.append(cur)
    return turns


def prosody(text:str,index:int):
    rate=-4;pitch=-1
    low=text.lower().strip()
    if text.rstrip().endswith('?'):
        rate+=2;pitch+=2;pause=560
    elif text.rstrip().endswith('!'):
        pause=500
    else:pause=520
    if low.startswith(('guarde','em resumo','pense','imagine','observe','agora','por enquanto','o ponto')):
        rate-=2
    rate+=(-1,0,1,0)[index%4]
    return f'{max(-10,min(4,rate)):+d}%',f'{max(-4,min(4,pitch)):+d}Hz',pause


async def synth(text,rate,pitch,path,sem):
    async with sem:
        for attempt in range(1,4):
            try:
                c=edge_tts.Communicate(text=text,voice=VOICE,rate=rate,pitch=pitch,volume='+0%')
                await asyncio.wait_for(c.save(str(path)),timeout=55)
                return
            except Exception:
                if attempt==3:raise
                await asyncio.sleep(.9*attempt)


async def main():
    if not SOURCE.exists():raise RuntimeError('RPD1.mp3 não encontrado')
    ROTEIROS.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True);TMP.mkdir(exist_ok=True)
    rows=transcribe()
    frozen=norm(' '.join(rows))
    (ROTEIROS/'RPD1-frozen.txt').write_text(
        '# RPD1 — transcrição automática congelada do MP3 original\n'
        '# Fonte de verdade: RPD1.mp3\n'
        '# Não houve resumo nem ampliação editorial.\n\n'+frozen+'\n',encoding='utf-8')
    turns=build_turns(rows)
    sem=asyncio.Semaphore(4);tasks=[];seq=[]
    for i,text in enumerate(turns):
        rate,pitch,pause=prosody(text,i);part=TMP/f'{i:03d}.mp3'
        seq.append((part,0 if i==len(turns)-1 else pause));tasks.append(synth(text,rate,pitch,part,sem))
    await asyncio.gather(*tasks)
    audio=AudioSegment.silent(duration=OPENING_SILENCE_MS)
    for part,pause in seq:
        audio+=AudioSegment.from_file(part,format='mp3')
        if pause:audio+=AudioSegment.silent(duration=pause)
    audio+=AudioSegment.silent(duration=ENDING_SILENCE_MS)
    audio=effects.compress_dynamic_range(audio,threshold=-20.0,ratio=2.0,attack=8.0,release=70.0)
    if audio.dBFS!=float('-inf'):audio=audio.apply_gain(TARGET_DBFS-audio.dBFS)
    if audio.max_dBFS>-1.2:audio=audio.apply_gain(-1.2-audio.max_dBFS)
    target=OUT/'rpd1-n2.mp3'
    audio.export(target,format='mp3',bitrate='128k',parameters=['-ac','1','-ar','44100'])
    spec={'voice':VOICE,'profile':'Padrão Sonoro Clínico Richelmy Murta — Sono em Dia / Ampulheta N2','version':VERSION,
          'source':'RPD1.mp3','frozen_transcript':'roteiros/RPD1-frozen.txt','text_integrity':'transcrição congelada sem reescrita editorial',
          'opening_silence_ms':OPENING_SILENCE_MS,'ending_silence_ms':ENDING_SILENCE_MS,'target_dbfs':TARGET_DBFS,
          'peak_ceiling_dbfs':-1.2,'format':'MP3 128 kbps, mono, 44.1 kHz','duration_seconds':round(len(audio)/1000,1)}
    (OUT/'audio-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.rmtree(TMP,ignore_errors=True)
    print(f'RPD N2 gerado: {spec["duration_seconds"]}s')

if __name__=='__main__':asyncio.run(main())
