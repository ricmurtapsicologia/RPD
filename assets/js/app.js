(()=>{
"use strict";
const VERSION="2.3.1";
const WHATSAPP="5535984640729";
const PAGE_URL="https://ricmurtapsicologia.github.io/RPD/";
const DRAFT_KEY="rpd_draft";
const DRAFT_SCHEMA=1;
const LEGACY_DRAFT_KEYS=["rpd_draft_v2_2_0","rpd_draft_v2_3_0"];

const EMOTIONS=["Ansiedade","Tristeza","Raiva","Culpa","Medo","Vergonha","Frustração","Insegurança","Desânimo","Solidão","Confusão","Alívio","Alegria","Outra"];

const DISTORTIONS=[
["Catastrofização","Imaginar um desfecho muito ruim como se fosse provável ou inevitável, mesmo quando existem outros resultados possíveis.","Se eu errar nesta apresentação, minha carreira acabou.","Estou tratando o pior cenário possível como se fosse o mais provável?"],
["Supergeneralização","Usar um episódio específico como prova de uma regra ampla sobre você, os outros ou o futuro.","Não consegui desta vez; eu nunca consigo nada.","Estou transformando um episódio em uma regra sobre sempre ou nunca?"],
["Leitura mental","Acreditar que sabe o que outra pessoa pensa ou sente sem evidências suficientes.","Ela ficou séria; com certeza acha que sou incompetente.","Tenho evidências do que a pessoa pensa ou estou preenchendo uma lacuna?"],
["Personalização","Assumir responsabilidade excessiva por um resultado que depende de vários fatores ou pessoas.","A reunião foi ruim porque eu estraguei tudo.","Estou assumindo responsabilidade por algo que também depende de outros fatores?"],
["Tudo ou nada","Avaliar pessoas ou situações em extremos, sem reconhecer graus intermediários.","Se não ficou perfeito, ficou péssimo.","Estou vendo apenas dois extremos quando existem gradações?"],
["Desqualificação do positivo","Diminuir ou invalidar evidências favoráveis para que elas não contem na avaliação.","Só elogiaram porque foram educados.","Estou descartando evidências positivas sem examiná-las com o mesmo rigor?"],
["Raciocínio emocional","Tratar o que você sente como prova suficiente de que algo é objetivamente verdadeiro.","Estou com medo, então deve haver perigo real.","Estou usando a intensidade do que sinto como prova do que aconteceu?"],
["Rotulação","Transformar um comportamento, erro ou dificuldade em uma definição rígida da pessoa inteira.","Cometi um erro; sou um fracasso.","Estou resumindo uma pessoa inteira a um rótulo?"],
["Filtro mental","Prender a atenção quase só a uma parte negativa e perder de vista o restante da situação.","Recebi vários retornos bons, mas só penso na única crítica.","Minha atenção está presa a um detalhe e ignorando o conjunto?"]
];

const SPECIAL_DISTORTIONS=[
["Não sei ainda","A classificação pode ficar em aberto. Isso é uma resposta válida."],
["Não identifiquei um padrão","Use quando nenhuma descrição parecer combinar de forma útil."]
];

const SEQUENCES={
  full:[1,2,3,4,5,6,7],
  essential:[1,2,3,5,7]
};

let step=1;
let mode="full";
let dirty=false;
let pendingAction=null;
let editingFromSummary=false;

const rangeTouched={
  before:false,
  beliefBefore:false,
  beliefAfter:false,
  after:false
};

const $=(selector,context=document)=>context.querySelector(selector);
const $$=(selector,context=document)=>Array.from(context.querySelectorAll(selector));
const val=id=>$("#"+id)?.value?.trim()||"";
const checked=name=>$$(`input[name="${name}"]:checked`).map(el=>el.value);

const toast=message=>{
  const el=$("#toast");
  if(!el)return;
  el.textContent=message;
  el.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer=setTimeout(()=>el.classList.remove("show"),3200);
};

const setText=(id,text,empty="Não informado")=>{
  const el=$("#"+id);
  if(el)el.textContent=(text||"").trim()||empty;
};

function localDate(){
  const now=new Date();
  const local=new Date(now.getTime()-now.getTimezoneOffset()*60000);
  return local.toISOString().slice(0,10);
}

function currentSequence(){
  return SEQUENCES[mode];
}

function escapeAttr(text){
  return String(text)
    .replace(/&/g,"&amp;")
    .replace(/"/g,"&quot;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;");
}


function enhanceMarkup(){
  const progressCard=$(".progress-card");
  if(progressCard){
    progressCard.id="progressCard";
    progressCard.setAttribute("role","progressbar");
    progressCard.setAttribute("aria-valuemin","1");
    progressCard.setAttribute("aria-valuemax","7");
    progressCard.setAttribute("aria-valuenow","1");
    progressCard.setAttribute("aria-valuetext","Etapa 1 de 7 · modo completo");
    $(".progress-track",progressCard)?.setAttribute("aria-hidden","true");
  }

  const form=$("#rpdForm");
  if(form && !$("#editReturnBar")){
    const bar=document.createElement("div");
    bar.id="editReturnBar";
    bar.className="edit-return-bar";
    bar.hidden=true;
    bar.innerHTML='<span>Você está editando um bloco da síntese.</span><button id="returnSummary" class="btn btn-secondary btn-small" type="button">Salvar alteração e voltar à síntese</button>';
    form.parentNode.insertBefore(bar,form);
  }

  const step5=$(".step[data-step=\"5\"]");
  if(step5){
    const title=$("h3",step5);
    if(title)title.id="step5Title";
    const intent=$(".stage-intent",step5);
    if(intent)intent.id="step5Intent";
    $(".inline-help",step5)?.classList.add("full-mode-only");
    $("#value")?.closest(".field")?.classList.add("full-mode-only");
    $("#distance")?.closest(".field")?.classList.add("full-mode-only");
    const actionLabel=$("label[for=\"action\"]",step5);
    if(actionLabel)actionLabel.id="actionLabel";
  }

  const response=$("#response");
  if(response){
    response.removeAttribute("required");
    const field=response.closest(".field");
    if(field && !$("#responsePending")){
      const pending=document.createElement("label");
      pending.className="response-pending";
      pending.innerHTML='<input id="responsePending" type="checkbox"> Ainda não consigo formular uma resposta alternativa neste momento.';
      response.after(pending);
    }
  }

  const badge=$(".print-badge");
  if(badge)badge.id="pModeBadge";
  const valuesHead=$("#pValues")?.previousElementSibling;
  if(valuesHead)valuesHead.id="pValuesHead";
  const thoughtSection=$("#pThought")?.closest(".print-section");
  if(thoughtSection && !$("#pInitialMeasures")){
    const section=document.createElement("section");
    section.className="print-section print-essential-only";
    section.hidden=true;
    section.innerHTML='<div class="print-section-head">3 · Medidas iniciais</div><div class="print-body" id="pInitialMeasures"></div>';
    thoughtSection.after(section);
  }
  [
    $("#pEvidenceGrid"),
    $("#pAlternative")?.closest(".print-section"),
    $("#pResponse")?.closest(".print-section"),
    ...$$(".print-change"),
    $("#pState")?.closest(".print-section")
  ].filter(Boolean).forEach(el=>el.classList.add("print-full-only"));
}

function setupChoices(){
  $("#emotionGrid").innerHTML=EMOTIONS.map((name,i)=>
    `<label class="choice"><input id="emotion_${i}" type="checkbox" name="emotion" value="${escapeAttr(name)}"><span>${name}</span></label>`
  ).join("");

  $("#distortionQuick").innerHTML=SPECIAL_DISTORTIONS.map(([name,description],i)=>
    `<label class="quick-choice"><input id="distortion_special_${i}" type="checkbox" name="distortion" value="${escapeAttr(name)}"><span><b>${name}</b><small>${description}</small></span></label>`
  ).join("");

  $("#distortionGrid").innerHTML=DISTORTIONS.map(([name,description,example,question],i)=>
    `<article class="distortion-option">
      <label class="distortion-select">
        <input id="distortion_${i}" type="checkbox" name="distortion" value="${escapeAttr(name)}" aria-label="${escapeAttr(name+": "+description)}">
        <span class="distortion-option-body">
          <span class="distortion-name">${name}</span>
          <span class="distortion-meaning">${description}</span>
        </span>
      </label>
      <details class="distortion-more">
        <summary>Como reconhecer e exemplo</summary>
        <div class="distortion-more-content">
          <span class="distortion-cue"><strong>Como perceber:</strong> ${question}</span>
          <span class="distortion-example-inline"><strong>Exemplo:</strong> ${example}</span>
        </div>
      </details>
    </article>`
  ).join("");

  const guide=$("#distortionGuideCards");
  if(guide){
    guide.innerHTML=DISTORTIONS.map(([name,description,example,question])=>
      `<article class="distortion-card"><b>${name}</b><p>${description}</p><p class="example"><strong>Exemplo:</strong> ${example}</p><p class="question"><strong>Pergunte-se:</strong> ${question}</p></article>`
    ).join("");
  }
}

function emotionLabels(){
  const values=checked("emotion").filter(v=>v!=="Outra");
  if(checked("emotion").includes("Outra")){
    const custom=val("otherEmotion");
    values.push(custom?`Outra: ${custom}`:"Outra");
  }
  return values;
}

function updateSelections(){
  const emotions=emotionLabels();
  const distortions=checked("distortion");
  $("#selectedEmotions").textContent=`Selecionados: ${emotions.length?emotions.join(", "):"nenhum"}.`;
  $("#selectedDistortions").textContent=`Padrões selecionados: ${distortions.length?distortions.join(", "):"nenhum"}.`;
  $("#otherEmotionWrap").hidden=!checked("emotion").includes("Outra");
}

function markRange(id,outId){
  rangeTouched[id]=true;
  const input=$("#"+id);
  const out=$("#"+outId);
  input.dataset.touched="true";
  out.textContent=`${input.value}/100`;
  out.classList.remove("is-empty");
  input.setAttribute("aria-valuetext",`${input.value} de 100`);
  dirty=true;
  saveDraft();
}

function bindRange(id,outId){
  const input=$("#"+id);
  const out=$("#"+outId);

  input.addEventListener("input",()=>markRange(id,outId));
  input.addEventListener("change",()=>markRange(id,outId));

  input.addEventListener("keydown",event=>{
    if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End","PageUp","PageDown"].includes(event.key)){
      markRange(id,outId);
    }
  });


  if(!rangeTouched[id]){
    out.textContent="Não avaliado";
    out.classList.add("is-empty");
    input.setAttribute("aria-valuetext","Não avaliado");
  }
}

function rangeText(id){
  return rangeTouched[id]?`${$("#"+id).value}/100`:"Não avaliado";
}

function autoGrow(el){
  el.style.height="auto";
  el.style.height=Math.min(el.scrollHeight,360)+"px";
}

function syncNavHeight(){
  const nav=$("nav");
  if(nav){
    document.documentElement.style.setProperty("--nav-h",`${Math.ceil(nav.getBoundingClientRect().height)}px`);
  }
}

function progress(){
  const seq=currentSequence();
  const index=seq.indexOf(step);
  const total=seq.length;
  const pos=Math.max(0,index)+1;

  const progressText=`${mode==="full"?"Etapa":"Passo"} ${pos} de ${total} · modo ${mode==="full"?"completo":"essencial"}`;
  $("#progressLabel").textContent=progressText;
  $("#progressBar").style.width=`${(pos/total)*100}%`;
  const progressCard=$("#progressCard");
  if(progressCard){
    progressCard.setAttribute("aria-valuemax",String(total));
    progressCard.setAttribute("aria-valuenow",String(pos));
    progressCard.setAttribute("aria-valuetext",progressText);
  }

  $$(".step").forEach(el=>{
    const stepNumber=Number(el.dataset.step);
    const position=seq.indexOf(stepNumber);
    const badge=$(".step-number",el);
    if(badge && position>=0)badge.textContent=String(position+1);
  });
}

function showStep(n,scroll=true){
  const seq=currentSequence();
  if(!seq.includes(n))n=seq[0];

  step=n;

  $$(".step").forEach(el=>{
    el.classList.toggle("is-active",Number(el.dataset.step)===step);
  });

  progress();

  if(step===7){
    renderSummary();
    editingFromSummary=false;
    $("#editReturnBar").hidden=true;
  }

  if(scroll){
    $("#form-area").scrollIntoView({behavior:"smooth",block:"start"});
  }
}

function navigate(delta){
  const seq=currentSequence();
  const index=seq.indexOf(step);
  const next=seq[index+delta];

  if(next===undefined)return;
  if(delta>0 && !validateStep(step))return;

  showStep(next);
}

function syncModeUi(){
  const essential=mode==="essential";
  $$(".full-mode-only").forEach(el=>el.hidden=essential);
  const title=$("#step5Title");
  const intent=$("#step5Intent");
  const actionLabel=$("#actionLabel");
  if(title)title.textContent=essential?"Próximo passo":"Valores e ação possível";
  if(intent)intent.textContent=essential
    ?"Escolha apenas um próximo passo pequeno e possível. Se não houver um agora, pode pular."
    :"Se fizer sentido, escolha uma direção de ação. Você pode pular esta parte.";
  if(actionLabel)actionLabel.innerHTML=essential
    ?'Qual pequeno próximo passo é possível agora? <span class="field-meta">opcional</span>'
    :'Qual pequena ação seria coerente com esse valor? <span class="field-meta">opcional</span>';
  const action=$("#action");
  if(action)action.placeholder=essential
    ?"Escolha algo pequeno, concreto e possível para agora."
    :"Escolha algo concreto, proporcional e possível.";
}

function mappedStepForMode(current,nextMode){
  const seq=SEQUENCES[nextMode];
  if(seq.includes(current))return current;
  return seq.find(n=>n>current) ?? seq[seq.length-1];
}

function setMode(nextMode,announce=true){
  if(!SEQUENCES[nextMode])return;
  const previousStep=step;
  mode=nextMode;
  const radio=$(nextMode==="full"?"#modeFull":"#modeEssential");
  if(radio)radio.checked=true;
  syncModeUi();
  const mapped=mappedStepForMode(previousStep,nextMode);
  if(mapped!==previousStep){
    showStep(mapped,false);
  }else{
    progress();
  }
  if(announce){
    toast(
      mode==="essential"
        ?"Modo essencial: menos passos e menos decisões de uma vez."
        :"Modo completo: sete etapas do RPD."
    );
  }
  saveDraft();
}

function clearErrors(root=document){
  $$(".has-error",root).forEach(el=>el.classList.remove("has-error"));
  $$(".field-error",root).forEach(el=>el.textContent="");
  $$("[aria-invalid=\"true\"]",root).forEach(el=>{
    el.removeAttribute("aria-invalid");
    const described=el.getAttribute("aria-describedby");
    if(described && described.endsWith("-error"))el.removeAttribute("aria-describedby");
  });
}

function fieldError(el,message){
  const field=el.closest(".field");
  if(field){
    field.classList.add("has-error");
    const box=$(".field-error",field);
    if(box){
      if(!box.id)box.id=`${el.id||"field"}-error`;
      box.textContent=message;
      el.setAttribute("aria-describedby",box.id);
    }
  }
  el.setAttribute("aria-invalid","true");
  el.focus();
}

function validateStep(n=step){
  const active=$(`.step[data-step="${n}"]`);
  if(!active)return true;

  clearErrors(active);

  for(const field of $$("[required]",active)){
    if(!field.value.trim()){
      fieldError(field,"Preencha este campo para continuar.");
      return false;
    }
  }

  if(n===2 && checked("emotion").length===0){
    toast("Selecione pelo menos uma emoção ou estado para continuar.");
    return false;
  }

  if(n===2 && checked("emotion").includes("Outra") && !val("otherEmotion")){
    fieldError($("#otherEmotion"),"Escreva qual emoção ou estado você quis acrescentar.");
    return false;
  }

  if(n===6 && mode==="full" && !val("response") && !$("#responsePending")?.checked){
    fieldError($("#response"),"Escreva uma resposta alternativa ou marque que ainda não consegue formulá-la.");
    return false;
  }

  return true;
}

function formState(){
  const state={
    schemaVersion:DRAFT_SCHEMA,
    appVersion:VERSION,
    step,
    mode,
    draftEnabled:$("#draftToggle").checked,
    fields:{},
    checks:{},
    rangeTouched:{...rangeTouched}
  };

  $$("#rpdForm input,#rpdForm textarea,#rpdForm select").forEach(el=>{
    if(el.type==="checkbox" || el.type==="radio"){
      state.checks[el.id]=el.checked;
    }else{
      state.fields[el.id]=el.value;
    }
  });

  return state;
}

function saveDraft(){
  if(!$("#draftToggle").checked)return;

  try{
    sessionStorage.setItem(DRAFT_KEY,JSON.stringify(formState()));
  }catch(e){}
}

function rangeOutId(id){
  return {
    before:"beforeOut",
    after:"afterOut",
    beliefBefore:"beliefBeforeOut",
    beliefAfter:"beliefAfterOut"
  }[id];
}

function readDraftRaw(){
  try{
    const current=sessionStorage.getItem(DRAFT_KEY);
    if(current)return current;
    for(const key of LEGACY_DRAFT_KEYS){
      const legacy=sessionStorage.getItem(key);
      if(legacy){
        sessionStorage.setItem(DRAFT_KEY,legacy);
        sessionStorage.removeItem(key);
        return legacy;
      }
    }
  }catch(e){}
  return null;
}

function removeDraft(){
  try{
    sessionStorage.removeItem(DRAFT_KEY);
    LEGACY_DRAFT_KEYS.forEach(key=>sessionStorage.removeItem(key));
  }catch(e){}
}

function syncResponsePending(){
  const pending=$("#responsePending");
  const response=$("#response");
  if(!pending || !response)return;
  response.disabled=pending.checked;
  response.setAttribute("aria-disabled",String(pending.checked));
}

function restoreDraft(){
  const raw=readDraftRaw();
  if(!raw)return;
  try{
    const data=JSON.parse(raw);
    if(!data.draftEnabled)return;
    if(data.schemaVersion && data.schemaVersion>DRAFT_SCHEMA){
      removeDraft();
      return;
    }
    $("#draftToggle").checked=true;
    Object.entries(data.fields||{}).forEach(([id,value])=>{
      const el=$("#"+CSS.escape(id));
      if(el)el.value=value;
    });
    Object.entries(data.checks||{}).forEach(([id,value])=>{
      const el=$("#"+CSS.escape(id));
      if(el)el.checked=Boolean(value);
    });
    Object.assign(rangeTouched,data.rangeTouched||{});
    for(const [id,touched] of Object.entries(rangeTouched)){
      const input=$("#"+id);
      const out=$("#"+rangeOutId(id));
      if(input && out && touched){
        input.dataset.touched="true";
        out.textContent=`${input.value}/100`;
        out.classList.remove("is-empty");
        input.setAttribute("aria-valuetext",`${input.value} de 100`);
      }
    }
    setMode(data.mode||"full",false);
    updateSelections();
    syncResponsePending();
    $$("textarea").forEach(autoGrow);
    showStep(currentSequence().includes(data.step)?data.step:1,false);
    toast("Rascunho desta aba restaurado.");
  }catch(e){
    removeDraft();
  }
}

function data(){
  return {
    identity:val("identity")||"Não informado",
    date:val("date"),
    situation:val("situation"),
    emotions:emotionLabels().join(", "),
    before:rangeText("before"),
    thought:val("thought"),
    beliefBefore:rangeText("beliefBefore"),
    distortions:checked("distortion").join(", ")||"Não classificado",
    supporting:val("supporting")||"Não informado",
    contrary:val("contrary")||"Não informado",
    alternative:val("alternative")||"Não informado",
    perspective:val("perspective")||"Não informado",
    status:val("status"),
    utility:val("utility"),
    value:mode==="essential"?"Não se aplica no modo essencial":val("value")||"Não informado",
    action:val("action")||"Não informado",
    distance:mode==="essential"?"Não se aplica no modo essencial":val("distance")||"Não informado",
    response:mode==="essential"
      ?"Não preenchida no modo essencial"
      :($("#responsePending")?.checked?"Ainda não consigo formular uma resposta alternativa neste momento.":val("response")),
    beliefAfter:mode==="essential"?"Não avaliado":rangeText("beliefAfter"),
    stateNow:mode==="essential"?"Não avaliado":val("stateNow")||"Não informado",
    after:mode==="essential"?"Não avaliado":rangeText("after")
  };
}

function makeGroup(title,editStep,items){
  const section=document.createElement("section");
  section.className="summary-group";

  const head=document.createElement("div");
  head.className="summary-group-head";

  const heading=document.createElement("h4");
  heading.textContent=title;

  const edit=document.createElement("button");
  edit.type="button";
  edit.className="btn btn-ghost btn-small edit-step";
  edit.dataset.step=String(editStep);
  edit.textContent="Editar";

  head.append(heading,edit);

  const list=document.createElement("div");
  list.className="summary-list";

  items.forEach(([label,value])=>{
    const row=document.createElement("div");
    row.className="summary-row";

    const strong=document.createElement("strong");
    strong.textContent=label;

    const span=document.createElement("span");
    span.textContent=value;

    row.append(strong,span);
    list.append(row);
  });

  section.append(head,list);
  return section;
}

function renderSummary(){
  const d=data();
  const summary=$("#summary");
  summary.innerHTML="";

  summary.append(
    makeGroup("O que aconteceu",1,[
      ["Situação",d.situation],
      ["Emoções ou estados",d.emotions],
      ["Desconforto antes",d.before]
    ])
  );

  summary.append(
    makeGroup("Como interpretei",3,[
      ["Pensamento automático",d.thought],
      ["Convicção inicial",d.beliefBefore],
      ["Padrões possíveis",d.distortions]
    ])
  );

  if(mode==="full"){
    summary.append(
      makeGroup("O que percebi ao investigar",4,[
        ["O que fez parecer verdadeiro",d.supporting],
        ["O que pode estar faltando",d.contrary],
        ["Outra explicação",d.alternative],
        ["Perspectiva externa",d.perspective],
        ["Status do pensamento",d.status],
        ["Utilidade percebida",d.utility]
      ])
    );
  }

  summary.append(
    makeGroup(mode==="full"?"Como quero responder":"O que posso fazer agora",5,
      mode==="full"
        ?[["Valor importante",d.value],["Pequena ação possível",d.action],["Se o pensamento não comandasse minha ação",d.distance]]
        :[["Próximo passo",d.action]]
    )
  );

  if(mode==="full"){
    summary.append(
      makeGroup("Nova leitura",6,[
        ["Resposta alternativa",d.response],
        ["Estado atual",d.stateNow]
      ])
    );
  }

  $("#beliefBeforeSummary").textContent=d.beliefBefore;
  $("#beliefAfterSummary").textContent=d.beliefAfter;
  $("#beforeSummary").textContent=d.before;
  $("#afterSummary").textContent=d.after;
}

function journeyValid(){
  for(const n of currentSequence().filter(n=>n!==7)){
    if(!validateStep(n)){
      showStep(n);
      return false;
    }
  }
  return true;
}

function message(kind="full"){
  const d=data();

  if(kind==="summary"){
    return [
      "RPD — resumo essencial",
      `Modo: ${mode==="full"?"completo":"essencial"}`,
      `Data: ${d.date}`,
      `Situação: ${d.situation}`,
      `Emoções/estados: ${d.emotions}`,
      `Pensamento automático: ${d.thought}`,
      `Convicção inicial: ${d.beliefBefore}`,
      `Próxima ação: ${d.action}`,
      mode==="full"?`Resposta alternativa: ${d.response}`:null,
      `Desconforto antes: ${d.before}`,
      mode==="full"?`Desconforto depois: ${d.after}`:null
    ].filter(Boolean).join("\n");
  }

  return [
    "Registro de Pensamentos — RPD",
    `Modo: ${mode==="full"?"completo":"essencial"}`,
    `Nome/iniciais: ${d.identity}`,
    `Data: ${d.date}`,
    `Situação: ${d.situation}`,
    `Emoções/estados: ${d.emotions}`,
    `Desconforto antes: ${d.before}`,
    `Pensamento automático: ${d.thought}`,
    `Convicção inicial: ${d.beliefBefore}`,
    `Padrões possíveis: ${d.distortions}`,
    mode==="full"?`O que fez o pensamento parecer verdadeiro: ${d.supporting}`:null,
    mode==="full"?`O que pode estar faltando: ${d.contrary}`:null,
    mode==="full"?`Outra explicação possível: ${d.alternative}`:null,
    mode==="full"?`Perspectiva externa: ${d.perspective}`:null,
    mode==="full"?`Valor importante: ${d.value}`:null,
    `${mode==="full"?"Pequena ação possível":"Próximo passo"}: ${d.action}`,
    mode==="full"?`Se o pensamento não comandasse a ação: ${d.distance}`:null,
    mode==="full"?`Resposta alternativa: ${d.response}`:null,
    mode==="full"?`Convicção agora: ${d.beliefAfter}`:null,
    mode==="full"?`Estado emocional atual: ${d.stateNow}`:null,
    mode==="full"?`Desconforto depois: ${d.after}`:null
  ].filter(Boolean).join("\n");
}

function openWhatsApp(kind){
  window.open(
    `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message(kind))}`,
    "_blank",
    "noopener,noreferrer"
  );
}

function buildPrint(){
  const d=data();
  const essential=mode==="essential";
  $$(".print-full-only").forEach(el=>el.hidden=essential);
  $$(".print-essential-only").forEach(el=>el.hidden=!essential);
  setText("pModeBadge",essential?"Modo essencial":"Modo completo");
  setText("pIdentity",d.identity);
  setText("pDate",d.date);
  setText("pEmotions",d.emotions);
  setText("pSituation",d.situation);
  setText(
    "pThought",
    essential
      ?`Pensamento automático: ${d.thought}\nConvicção inicial: ${d.beliefBefore}\nPadrões possíveis: ${d.distortions}`
      :`Pensamento automático: ${d.thought}\nConvicção inicial: ${d.beliefBefore}\nPadrões possíveis: ${d.distortions}\nClassificação atual: ${d.status}\nUtilidade percebida: ${d.utility}`
  );
  setText("pInitialMeasures",`Desconforto inicial: ${d.before}\nConvicção inicial: ${d.beliefBefore}`);
  setText("pSupporting",d.supporting);
  setText("pContrary",d.contrary);
  setText("pAlternative",`Outra explicação: ${d.alternative}\nPerspectiva externa: ${d.perspective}`);
  setText("pValuesHead",essential?"4 · Próximo passo":"6 · Valores e ação possível");
  setText(
    "pValues",
    essential
      ?`Próximo passo: ${d.action}`
      :`Valor importante: ${d.value}\nPequena ação possível: ${d.action}\nSe o pensamento não comandasse a ação: ${d.distance}`
  );
  setText("pResponse",d.response);
  setText("pBeliefBefore",d.beliefBefore);
  setText("pBeliefAfter",d.beliefAfter);
  setText("pBefore",d.before);
  setText("pAfter",d.after);
  setText("pState",`Estado emocional atual: ${d.stateNow}`);
  $("#pEvidenceGrid").classList.toggle("stack",(d.supporting.length+d.contrary.length)>900);
  const now=new Date();
  setText(
    "pGenerated",
    `Gerado em ${now.toLocaleDateString("pt-BR")} às ${now.toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}`
  );
}

function openDialog(id){
  const dialog=$("#"+id);
  if(dialog && !dialog.open)dialog.showModal();
}

function closeDialog(dialog){
  if(dialog?.open)dialog.close();
}

function action(title,text,callback){
  pendingAction=callback;
  $("#actionTitle").textContent=title;
  $("#actionText").textContent=text;
  openDialog("actionDialog");
}

function rangeOutId(id){
  return {
    before:"beforeOut",
    after:"afterOut",
    beliefBefore:"beliefBeforeOut",
    beliefAfter:"beliefAfterOut"
  }[id];
}

function resetRanges(){
  for(const id of Object.keys(rangeTouched)){
    rangeTouched[id]=false;

    const input=$("#"+id);
    if(input){
      input.value="50";
      input.dataset.touched="false";
      input.setAttribute("aria-valuetext","Não avaliado");
    }

    const out=$("#"+rangeOutId(id));
    if(out){
      out.textContent="Não avaliado";
      out.classList.add("is-empty");
    }
  }
}

function clearForm(){
  $("#rpdForm").reset();
  $$('#rpdForm input[type="checkbox"]').forEach(el=>el.checked=false);

  $("#date").value=localDate();

  resetRanges();

  removeDraft();
  editingFromSummary=false;
  $("#editReturnBar").hidden=true;
  syncResponsePending();

  dirty=false;
  setMode("full",false);
  updateSelections();

  $$("textarea").forEach(el=>el.style.height="");
  showStep(1);
}

function handleDistortionChange(target){
  const specials=SPECIAL_DISTORTIONS.map(item=>item[0]);

  if(specials.includes(target.value) && target.checked){
    $$("input[name=\"distortion\"]").forEach(el=>{
      if(el!==target)el.checked=false;
    });
  }else if(target.checked){
    $$("input[name=\"distortion\"]").forEach(el=>{
      if(specials.includes(el.value))el.checked=false;
    });
  }

  updateSelections();
}

function bindEvents(){
  document.addEventListener("change",event=>{
    const target=event.target;

    if(target.name==="mode"){
      setMode(target.value);
    }

    if(target.matches("input[name=\"emotion\"]")){
      updateSelections();
    }

    if(target.matches("input[name=\"distortion\"]")){
      handleDistortionChange(target);
    }

    if(target.id==="responsePending"){
      syncResponsePending();
      clearErrors(target.closest(".field")||document);
    }

    if(target.id==="draftToggle"){
      if(target.checked){
        saveDraft();
        toast("Rascunho será mantido somente nesta aba.");
      }else{
        removeDraft();
        toast("Rascunho temporário desativado.");
      }
    }

    if(target.closest("#rpdForm")){
      dirty=true;
      saveDraft();
    }
  });

  document.addEventListener("input",event=>{
    const target=event.target;

    if(target.matches("textarea")){
      autoGrow(target);
    }

    if(target.id==="otherEmotion"){
      updateSelections();
    }

    if(target.closest("#rpdForm") && !target.matches("input[type=\"range\"]")){
      dirty=true;
      saveDraft();
    }
  });

  $$(".next").forEach(btn=>btn.addEventListener("click",()=>navigate(1)));
  $$(".prev").forEach(btn=>btn.addEventListener("click",()=>navigate(-1)));

  $("#skipValues")?.addEventListener("click",()=>navigate(1));
  $("#returnSummary")?.addEventListener("click",()=>{
    if(!editingFromSummary)return;
    if(!validateStep(step))return;
    editingFromSummary=false;
    $("#editReturnBar").hidden=true;
    showStep(7);
  });

  document.addEventListener("click",event=>{
    const opener=event.target.closest("[data-open-dialog]");
    if(opener)openDialog(opener.dataset.openDialog);

    const closer=event.target.closest("[data-close-dialog]");
    if(closer)closeDialog(closer.closest("dialog"));

    const edit=event.target.closest(".edit-step");
    if(edit){
      const target=Number(edit.dataset.step);
      if(currentSequence().includes(target)){
        editingFromSummary=true;
        $("#editReturnBar").hidden=false;
        showStep(target);
      }else{
        toast("Esse bloco faz parte do modo completo.");
      }
    }
  });

  $("#loadVideo").addEventListener("click",()=>{
    const slot=$("#videoSlot");
    slot.className="video-wrap";
    slot.innerHTML='<iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/qp8VUlVqooI?rel=0" title="Como fazer um Registro de Pensamentos" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
  });

  $("#shareRecord").addEventListener("click",()=>{
    if(journeyValid())openDialog("shareDialog");
  });

  $("#shareSummary").addEventListener("click",()=>{
    closeDialog($("#shareDialog"));
    openWhatsApp("summary");
  });

  $("#shareFull").addEventListener("click",()=>{
    closeDialog($("#shareDialog"));
    openWhatsApp("full");
  });

  $("#printPdf").addEventListener("click",()=>{
    if(!journeyValid())return;

    action(
      "Salvar ou imprimir PDF",
      "A versão pode conter informações pessoais e emocionais. Revise o local onde será salva.",
      ()=>{
        buildPrint();
        window.print();
      }
    );
  });

  window.addEventListener("beforeprint",buildPrint);

  $("#newRecord").addEventListener("click",()=>
    action(
      "Iniciar novo registro",
      "Isso limpará as respostas atuais nesta aba.",
      clearForm
    )
  );

  $("#actionConfirm").addEventListener("click",()=>{
    const fn=pendingAction;
    pendingAction=null;
    closeDialog($("#actionDialog"));
    if(fn)fn();
  });

  $("#sharePage").addEventListener("click",async()=>{
    const text="RPD — ferramenta psicoeducativa para organizar situação, emoções, pensamentos e próximos passos.";

    try{
      if(navigator.share){
        await navigator.share({title:"RPD",text,url:PAGE_URL});
      }else if(navigator.clipboard){
        await navigator.clipboard.writeText(PAGE_URL);
        toast("Link copiado.");
      }else{
        window.prompt("Copie o link:",PAGE_URL);
      }
    }catch(e){}
  });

  $("#contactBtn").addEventListener("click",()=>{
    const name=val("contactName");
    const msg=val("contactMessage");

    if(!msg){
      toast("Escreva uma mensagem antes de abrir o WhatsApp.");
      $("#contactMessage").focus();
      return;
    }

    const text=`Olá${name?", prefiro ser chamado(a) de "+name:""}. ${msg}`;

    window.open(
      `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(text)}`,
      "_blank",
      "noopener,noreferrer"
    );
  });

  $$("dialog").forEach(dialog=>{
    dialog.addEventListener("click",event=>{
      if(event.target===dialog)closeDialog(dialog);
    });
  });

  window.addEventListener("beforeunload",event=>{
    if(dirty && !$("#draftToggle").checked){
      event.preventDefault();
      event.returnValue="";
    }
  });

  window.addEventListener("resize",syncNavHeight);
}

function init(){
  enhanceMarkup();
  setupChoices();
  syncNavHeight();

  bindRange("before","beforeOut");
  bindRange("after","afterOut");
  bindRange("beliefBefore","beliefBeforeOut");
  bindRange("beliefAfter","beliefAfterOut");

  $("#date").value=localDate();

  updateSelections();
  syncResponsePending();
  setMode("full",false);
  progress();
  bindEvents();
  restoreDraft();

  $$("textarea").forEach(el=>{
    el.addEventListener("input",()=>autoGrow(el));
  });
}

if(document.readyState==="loading"){
  document.addEventListener("DOMContentLoaded",init);
}else{
  init();
}
})();
