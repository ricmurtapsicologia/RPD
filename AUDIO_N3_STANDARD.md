# N3 Natural — RPD

Versão: `n3-20260831` • Perfil: `N3-C`.

A fonte textual canônica é `roteiros/RPD1-frozen.txt`, já congelada a partir do MP3 original. O N3 não retranscreve o áudio original em cada build: isso evita deriva de ASR e garante reprodutibilidade.

Regras: Neural TTS pt-BR `pt-BR-AntonioNeural`; unidades respiratórias; prosódia por intenção semântica; mono 44,1 kHz; MP3 128 kbps; alvo -18 dBFS; pico <= -1,2 dBFS; nenhum ambiente/Foley; player HTML5; N2 preservado para rollback.
