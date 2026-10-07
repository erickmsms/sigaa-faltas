---
name: sigaa-faltas
description: Levanta a frequência de todas as disciplinas do semestre no SIGAA da UFPE (Plano de Curso + Alunos → Frequência), cruza com as faltas previstas do aluno e gera um relatório de quantas faltas ainda cabem em cada disciplina, indicando quais professores não registram chamada ou não têm plano de curso. Use quando o usuário perguntar quantas faltas ainda pode ter, pedir o relatório de frequência do SIGAA, quiser cadastrar uma falta prevista (viagem, consulta etc.) ou anotar uma falta que já teve em disciplina cujo professor não registra chamada ("faltei X hoje").
---

# SIGAA – relatório de faltas

Todos os caminhos abaixo são relativos à pasta desta skill (onde está este `SKILL.md`).

```
dados/periodos/<semestre>.toml          ← faltas previstas, faltas anotadas e feriados
dados/periodos/<semestre>.turmas.json   ← dados coletados do SIGAA (você gera)
dados/relatorios/<semestre>_<data>.md   ← relatórios gerados
modelo-periodo.toml                     ← modelo para um semestre novo
exemplo/                                ← exemplo fictício completo (formato de todos os arquivos)
scripts/faltas.py                       ← faz a conta (Python 3.11+, sem dependências)
```

**Privacidade:** os dados do aluno ficam só em `dados/`, que é ignorada pelo git da skill.
Nunca coloque dados pessoais fora de `dados/` nem faça commit deles no repositório da skill.
Se `dados/` for um repositório git próprio (backup privado do aluno), faça commit e push
**lá** depois de cada alteração. Se não for, apenas salve os arquivos.

O usuário pode não ser da área de computação: fale em português simples, sem jargão
(não mencione TOML, JSON, commit etc., a menos que ele pergunte). Ele não precisa editar
arquivos — você edita por ele.

## Primeiro uso

Se `dados/` não existir, crie `dados/periodos/` e `dados/relatorios/` e siga o modo D.

## Modos de uso

### A) Anotar uma falta que já aconteceu

Quando o usuário disser que faltou a uma aula ("faltei cálculo hoje", "faltei dia 15/09
em física"), principalmente em disciplinas cujo professor não registra chamada no SIGAA
(`registra_chamada: false`), ele precisa controlar essas faltas por conta própria:

1. Acrescente um bloco `[[faltas_manuais]]` no `dados/periodos/<semestre>.toml`:
   `disciplina` (código como `MAT001` ou trecho do nome), `data`, e opcionalmente
   `aulas` (padrão: todos os horários da disciplina naquele dia da semana) e `motivo`.
   Uma entrada por dia.
2. Rode o script (passo 5 do modo D) e confira que a falta entrou: ela aparece como
   "+ N anotadas" na coluna de faltas já tidas. Se aparecer um alerta ❓ (disciplina
   ambígua ou dia sem aula), corrija a entrada.
3. Mostre ao usuário como ficou a disciplina.

Se o professor depois lançar essa falta no SIGAA, a data passa a constar em
`datas_faltas_registradas` do `.turmas.json` e o script não conta duas vezes.

### B) Cadastrar uma falta prevista

Se o usuário quer registrar uma ausência futura ("vou faltar dia X", "vou viajar de A a B"):

1. Descubra o semestre atual (o mais recente em `dados/periodos/`, ou pergunte).
2. Acrescente um bloco `[[ausencias]]` no `.toml` do semestre. Datas `de`/`ate` são
   inclusivas; para um dia só use `de = ate`.
   Ausências que valem só para uma disciplina vão como `[[faltas_manuais]]` (modo A),
   mesmo que sejam futuras.
3. Se já existe o `.turmas.json` do semestre, rode o script (passo 5 do modo D) para mostrar
   o impacto sem entrar no SIGAA de novo. Se não existe, ofereça o relatório completo.

### C) Tirar uma disciplina da análise

Algumas disciplinas não têm aula nem controle de frequência (monitoria que só contabiliza
horas, estágio, TCC, atividades complementares…). Quando o usuário disser algo como
"monitoria não tem aula, pode desconsiderar":

1. Acrescente no `.toml` do semestre:

   ```toml
   [[sem_frequencia]]
   disciplina = "IF791"        # código ou trecho do nome
   motivo = "Só contabiliza horas de monitoria"
   ```

2. Rode o script: a disciplina sai da tabela e dos alertas e aparece só na linha
   "Fora da análise".

### D) Relatório completo (entra no SIGAA)

1. **Período.** Se não existir `dados/periodos/<semestre>.toml` para o semestre atual,
   copie `modelo-periodo.toml`, preencha `semestre`, `inicio`, `fim` (datas que aparecem
   em "Turmas do Semestre" no portal) e os feriados do calendário acadêmico (link
   "Calendário Acadêmico" no portal), e pergunte ao usuário se ele tem faltas previstas.

2. **Login.** Abra `https://sigaa.ufpe.br/sigaa/` no navegador que você controla (o navegador
   embutido do app Claude, ou o Claude in Chrome). Peça para o usuário fazer login ele mesmo
   e avisar. **Nunca digite nem peça a senha.** Se não houver navegador disponível, peça
   prints das páginas (Plano de Curso e Frequência de cada disciplina).

3. **Portal do discente.** Leia a seção "Turmas do Semestre": nome de cada disciplina e o
   código de horário (ex.: `3M56 5M34`, `6M3456`, `56M1 6N4`).
   Formato do horário: dígitos iniciais = dias (2=seg … 7=sáb), letra = turno (M/T/N),
   dígitos finais = horários; **cada horário = 1 aula de 50 min**.

4. **Para cada disciplina** (abra a primeira pelo link com o nome; para as seguintes use o
   botão "Trocar de turma" no topo, que abre uma lista `CÓDIGO - NOME (CHh)` — anote a CH):
   - **Página principal da turma**: costuma ter o cronograma (tabela de datas ou lista de
     tópicos `Assunto (dd/mm - dd/mm)`) e o quadro "Avaliações".
   - **Turma → Plano de Curso**: veja se existe ("Esta turma ainda não possui um plano
     cadastrado" = sem plano) e leia o cronograma/avaliações.
   - **Alunos → Frequência**: tabela `Data | Situação` (`Presente`, `N Falta(s)`,
     `Não Registrada`). Se aparecer "A frequência ainda não foi lançada" ou não houver
     nenhum registro, o professor **não registra chamada**.
   - Se a disciplina parecer não ter aula (monitoria, estágio, TCC, atividades
     complementares, sem horário ou sem tópicos de aula), pergunte ao usuário se ela deve
     ficar fora da análise (modo C).
   - Dicas de navegação: o SIGAA é lento — depois de cada clique espere ~3 s antes de ler
     a página. Os itens do menu lateral (Plano de Curso, Frequência) só ficam clicáveis
     depois de expandir o grupo ("Turma" ou "Alunos").

5. **Monte `dados/periodos/<semestre>.turmas.json`** (formato em `exemplo/2026.2.turmas.json`):
   - `faltas_registradas`: soma das faltas na página de Frequência.
   - `datas_faltas_registradas`: as datas com `N Falta(s)`.
   - `registra_chamada`: `false` se a frequência não foi lançada.
   - `tem_plano`: `false` se o Plano de Curso não existe.
   - `sem_aula`: datas **dentro das ausências previstas** em que o horário semanal teria aula
     mas o cronograma do professor não lista aula. Deixe vazio se não há cronograma.
   - `eventos`: provas, apresentações, entregas etc. com data (do cronograma/avaliações).

   Depois rode:

   ```bash
   python scripts/faltas.py dados/periodos/<semestre>.toml dados/periodos/<semestre>.turmas.json --hoje AAAA-MM-DD
   ```

   O script imprime o relatório. Salve em `dados/relatorios/<semestre>_<AAAA-MM-DD>.md`.
   Se não houver Python 3.11+, ofereça instalar; se o usuário não quiser, faça a conta
   você mesmo seguindo as regras abaixo.

6. **Responda ao usuário** com a tabela e os alertas, deixando explícito:
   - quais disciplinas **não registram chamada** e quais **não têm plano de curso** —
     lembre o usuário de te avisar quando faltar nessas (modo A);
   - disciplinas que ficaram fora da análise (sem frequência);
   - disciplinas em risco (sobra menos de 1 dia de aula);
   - provas/apresentações que caem em dias de falta prevista;
   - premissas (feriados considerados, datas "sem aula" que podem mudar).

## Regras de cálculo (UFPE)

- Aula = 50 min. Total de aulas = CH em horas × 60 / 50 (60h → 72 aulas; 45h → 54).
- Frequência mínima 75% ⇒ máximo de faltas = total − ⌈0,75 × total⌉ (72 → 18; 54 → 13).
- Disciplinas em `[[sem_frequencia]]` não entram na conta.
- Faltas já tidas = faltas lançadas no SIGAA + `[[faltas_manuais]]` cujas datas não
  estão lançadas no SIGAA.
- Faltas futuras = horários do código de horário que caem nas datas das `[[ausencias]]`,
  dentro de `inicio`–`fim`, menos `[[feriados]]`, menos `sem_aula` da disciplina e menos
  dias já anotados como falta manual.
- "Pior caso" = conta também as datas `sem_aula` e os `[[feriados_incertos]]`.
- Os totais "Aulas (Ministradas/Total)" da página da turma às vezes diferem da CH;
  o SIGAA usa a CH para o percentual, então use a CH.
