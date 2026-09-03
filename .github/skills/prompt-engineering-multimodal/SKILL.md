---
name: prompt-engineering-multimodal
description: >-
  Metodologia acionável de engenharia de prompt multimodal (texto + imagem + áudio),
  destilada do livro "The Art of Prompt Engineering for Multimodal AI" (Yash Jain, 2025).
  Use quando o usuário quiser criar, revisar ou otimizar prompts que combinam texto, imagem e
  áudio (referência: GPT-4/CLIP/AudioLM e equivalentes modernos), ou pedir frameworks/templates
  de prompt para conteúdo multimodal, storytelling integrado ou geração criativa.
metadata:
  source: "Jain Y. The Art of Prompt Engineering for Multimodal AI (2025) — resumo/adaptação, não reprodução"
  models_ref: "GPT-4 (texto), CLIP (imagem↔texto), AudioLM (áudio)"
  lang: pt-BR
---

# Prompt Engineering Multimodal

Engenharia de prompt para guiar modelos multimodais a produzir conteúdo **coeso** em texto,
imagem e áudio. O objetivo não é só qualidade em cada mídia, mas **harmonia entre elas**.

## Modelos de referência (função típica)

| Modo | Modelo (livro) | Papel | O que o prompt deve guiar |
|------|----------------|-------|---------------------------|
| Texto | GPT-4 | Espinha dorsal linguística (contexto/narrativa) | tom, estilo, estrutura, profundidade |
| Imagem | CLIP | Ponte texto↔imagem (interpretação/generação visual) | sujeito, atributos visuais, contexto, estética |
| Áudio | AudioLM | Dimensão sonora (soundscape, música, voz) | atmosfera, emoção, camadas, ritmo |

> Princípios abaixo são **agnósticos de modelo**; os exemplos citam os modelos do livro, mas
> aplicam-se a ferramentas modernas equivalentes (ex.: GPT‑4o, DALL·E, Stable Diffusion,
> Midjourney, Veo/AudioLM, ElevenLabs etc.).

## Princípios universais de prompt

1. **Clareza e especificidade** — diretiva explícita do que se espera; evite ambiguidade.
2. **Contexto** — forneça cenário/background quando a tarefa exigir compreensão fina.
3. **Estrutura** — organize: (A) Introdução do cenário → (B) Tarefa/resultado → (C) Restrições.
4. **Equilíbrio especificidade × liberdade criativa** — detalhe o bastante para guiar, deixe
   margem para interpretação; ajuste iterativamente.
5. **Iteração** — refine com base nos outputs (feedback loop), mudando **um elemento por vez**.

## Workflow recomendado (6 passos)

1. **Defina a intenção** — o que o usuário quer criar/gerar e para quê.
2. **Escolha a(s) modalidade(s)** — texto, imagem, áudio ou integração; identifique o modelo.
3. **Estruture o prompt por modalidade** (ver templates abaixo).
4. **Integre** (se multimídia): tema unificado + descritores complementares + sincronização.
5. **Gere e analise** — avalie cada mídia isolada e em conjunto (tom, tema, ritmo).
6. **Refine** — repita o loop: analisar → ajustar um elemento → validar.

---

## A. Template — Prompt de texto (GPT-4)

```
A. Introdução: <cenário/contexto em 1-2 frases>
B. Tarefa: <o que gerar + formato/saída esperada>
C. Restrições: <tom, estilo, extensão, o que evitar>
```

Técnicas:
- **Few-shot**: inclua 1–3 exemplos do formato/estilo desejado.
- **Zero-shot**: instruções claras e auto-contidas, sem exemplos.
- **Chain-of-thought**: peça raciocínio passo a passo para problemas/multicamadas.
- **Reframing criativo**: troque o ângulo, use analogias/metáforas.
- **Refinamento iterativo**: ajuste tom, detalhe e ambiguidade a cada rodada.

---

## B. Template — Prompt de imagem (CLIP / DALL·E etc.)

Fórmula em camadas (da base à estética):

1. **Sujeito central** — o elemento principal (ex.: "uma cidade futurista").
2. **Atributos descritivos** — cor, humor, textura, iluminação (ex.: "neon vibrante", "névoa").
3. **Contexto / ambiente** — hora do dia, clima, cenário ao redor (ex.: "ruas encharcadas à noite").
4. **Influência artística (opcional)** — estilo, período, artista (ex.: "em estilo impressionista").

Exemplos do livro (resumidos):
- Urbano: *"cityscape futurista envolto em névoa, arranha-céus de neon, ruas desertas encharcadas de chuva."*
- Natureza: *"floresta tranquila ao amanhecer, raios suaves de sol entre a névoa, flores silvestres."*
- Surreal: *"fusão abstrata de formas geométricas e orgânicas sob um céu vibrante e ondulante."*

> Variações pequenas de detalhe mudam muito o resultado — teste níveis de detalhe diferentes.

---

## C. Template — Prompt de áudio (AudioLM)

Estrutura em sequência:
```
A. Atmosfera geral: <mood/estilo/contexto>   ex.: "soundscape sereno e atmosférico"
B. Corpo: <instrumentos/sons/voz e qualidades> ex.: "piano suave + sons de natureza"
C. Resolução: <como o áudio termina/desvanece>
```

Descritores sensoriais úteis: melódico, etéreo, pulsante, sussurrante, rústico, espacial.
Para **blend soundscape + narrativa**:
- **Camadas**: comece pelo fundo (ex.: "noite chuvosa, trovão distante"), depois o primeiro plano ("voz introspectiva narrando..."), e indique a **proeminência** relativa de cada camada.
- **Sequência temporal**: defina a evolução (ex.: ambiente → entra a voz → o som reemerge no fim).
- **Alinhamento emocional**: tom do soundscape deve reforçar o da voz.

---

## D. Integração cross-modal (harmonizar texto + imagem + áudio)

1. **Tema unificado** — um conceito central que amarra as três mídias.
2. **Descritores complementares** — palavras que se estendem entre modos (ex.: "sereno e onírico" vale para imagem e som).
3. **Estrutura por modalidade** — texto: narrativa/contexto; imagem: cor/composição/estilo; áudio: ritmo/pitch/humor.
4. **Sincronização** — tom/estilo consistentes; pistas temporais e espaciais casadas (ex.: "cidade agitada ao crepúsculo" → visual noturno + soundscape urbano).
5. **Transições** — frases-ponte que levam de uma mídia à outra (ex.: "...conforme a noite cai" → imagem de crepúsculo + áudio mais suave).
6. **Checagens de sincronia** — compare os outputs entre mídias; corrija disparidades de tema/tom/ritmo.

Workflows úteis: plataformas de integração unificada; **processamento modular** (gerar cada mídia separada + camada de integração); versionamento; pipeline de testes conjunto.

---

## E. Estratégias avançadas

- **Fusão conceitual** — combine forças: GPT-4 define contexto → CLIP captura atmosfera visual → AudioLM evoca emoção; use frases-ponte ("imagine esta cena acompanhada de...").
- **Analogias, metáforas e simbolismo consistentes** — um símbolo usado no texto deve ecoar na imagem e no áudio (ex.: "luz = esperança"; "uma tela de segredos sussurrados" → mistério visual + sutileza sonora).
- **Refinamento estruturado** — avalie o conjunto, ajuste **um elemento por vez** (linguagem → cor/composição → humor/ritmo), colete feedback (revisão ou ferramentas) e **documente** o que mudou; itere até o equilíbrio.

## F. Personalização

1. Defina a **identidade criativa** do usuário (paleta, tom, temas recorrentes).
2. Traduza em **marcadores por modalidade**: texto → tom/marcadores estilísticos; imagem → estilos/eras e ambiente; áudio → atmosfera/instrumentos/qualidade vocal.
3. Mantenha um **fio temático único** nas três mídias.
4. Itere até o output carregar a "assinatura" do usuário sem engessar o modelo.

Exemplos do livro (conceito → obra): "Floresta Encantada" (narrativa de folclore + luz etérea + sons naturais com tons etéreos) e "Sinfonia Urbana" (narrativa tecnológica + arquitetura ousada/neon + trilha com batidas urbanas).

---

## G. Ética, legal e responsabilidade (checar antes de entregar)

- **Transparência/accountability** — processos explicáveis; criador responsável pelo output.
- **Viés e justiça** — vigiar outputs para não reforçar vieses; representação equitativa.
- **Propriedade intelectual** — cuidado com copyright/autoria em conteúdo gerado que mistura fontes.
- **Privacidade/segurança** — não expor dados pessoais/proprietários em prompts.
- **Sensibilidade cultural** — considerar contexto cultural dos temas.

---

## Checklist de qualidade (antes de finalizar)

- [ ] Clareza: diretiva explícita, sem ambiguidade
- [ ] Contexto suficiente para o resultado desejado
- [ ] Estrutura lógica (Introdução/Tarefa/Restrições) ou fórmula da modalidade aplicada
- [ ] Especificidade e liberdade criativa equilibradas
- [ ] Multi-mídia: tema unificado + tom/ritmo sincronizados + transições
- [ ] Loop iterativo executado (≥1 refinamento com mudança única documentada)
- [ ] Sem vieses/segredos/questões de IP evidentes
- [ ] Output conferido contra a intenção do usuário

## Glossário (resumo do livro)

- **Multimodal AI**: sistemas que processam/geram múltiplos tipos de dados (texto, imagem, áudio).
- **Prompt engineering**: prática de desenhar prompts para otimizar outputs de IA.
- **Cross-modal learning**: transferência de conhecimento entre tipos de dados (texto influencia imagem).
- **Conceptual fusion**: combinar ideias/temas em um único output integrado.
- **Iterative refinement**: melhoria contínua via ajustes repetidos do prompt.
