# 📅 Quantas faltas ainda posso ter? (SIGAA / UFPE)

Uma ferramenta para **qualquer estudante da UFPE**, de qualquer curso, que responde de
forma simples:

> **"Quantas aulas eu ainda posso faltar em cada disciplina sem reprovar por falta?"**

Você conversa em português com o [Claude](https://claude.com/claude-code), um assistente
de inteligência artificial. Ele entra no SIGAA junto com você, olha a frequência de todas
as suas disciplinas, desconta as faltas que você **já sabe que vai ter** (uma viagem, um
congresso, uma consulta) e te entrega um relatório pronto.

**Você não precisa saber programar.**

---

## Para que serve

O SIGAA mostra a sua frequência, mas **não diz quanto você ainda pode faltar**. Além disso:

- muitos professores **não lançam a chamada** no SIGAA durante o semestre. Aí parece que
  você tem 100% de presença, mas na verdade ninguém está contando;
- se você vai viajar, precisa conferir, disciplina por disciplina, quais aulas vai perder,
  quantas aulas cada dia vale, se algum dia é feriado…

Esta ferramenta faz tudo isso por você e avisa, por exemplo:

- 🔴 em quais disciplinas você está **perto de reprovar por falta**;
- 📌 se alguma **prova ou apresentação** cai num dia em que você vai faltar;
- ⚪ quais professores **não registram chamada** no SIGAA (nessas, você mesmo precisa
  anotar suas faltas, e a ferramenta te ajuda);
- ⚪ quais disciplinas **não têm plano de curso** cadastrado.

## Como é o resultado

Exemplo com dados **fictícios** (alguém que vai a um congresso de 26/10 a 30/10):

| Disciplina | Chamada | Plano | Faltas já tidas | Faltas previstas | Total / limite | Ainda pode faltar |
|---|---|---|---|---|---|---|
| Cálculo 1 | ✅ | ✅ | 2 | 2 (26/10) | 4 / 18 | **14 aulas** (7 dias) |
| Física Geral 1 | ✅ | ❌ sem plano | 14 | 4 (27/10, 29/10) | 18 / 18 | **0 aulas** (0 dias) |
| Inglês Instrumental | ❌ não registra | ✅ | 0 + 2 anotadas | 2 (30/10) | 4 / 9 | **5 aulas** (2 dias) |
| Introdução à Administração | ❌ não registra | ✅ | 0 + 2 anotadas | 2 (27/10) | 4 / 18 | **14 aulas** (7 dias) |

**Alertas**
- 🔴 **Física Geral 1**: você fica exatamente no limite. Qualquer falta a mais reprova.
- 📌 **Cálculo 1**: 28/10 é dia da 1ª prova, e você estará no congresso.

O relatório completo do exemplo está em [`exemplo/relatorio.md`](exemplo/relatorio.md).

---

## O que você precisa

1. **O app do Claude** no computador (Windows ou Mac), baixado em
   [claude.com/download](https://claude.com/download), com um **plano pago** (Pro ou
   superior), que é o que libera a aba **Code**.
2. Seu login do SIGAA. **Você mesmo digita a senha**: o Claude nunca vê nem pede sua senha.

Só isso. Se faltar alguma outra coisa no seu computador (por exemplo, o Python), o
próprio Claude avisa e te ajuda a instalar.

## Como instalar (uma vez só)

1. Abra o app do Claude e vá na aba **Code**.
2. Copie e cole esta mensagem:

   ```
   Instale a skill https://github.com/erickmsms/sigaa-faltas na minha pasta de skills do Claude (~/.claude/skills/sigaa-faltas)
   ```

3. Pronto. Nas próximas conversas o Claude já sabe usar a ferramenta.

<details>
<summary>Prefere instalar pelo terminal?</summary>

```bash
git clone https://github.com/erickmsms/sigaa-faltas.git ~/.claude/skills/sigaa-faltas
```
</details>

## Como usar

É só conversar com o Claude na aba **Code**. Alguns exemplos:

| Você diz… | O que acontece |
|---|---|
| *"Quantas faltas ainda posso ter?"* | O Claude abre o SIGAA, você faz login, ele passa por todas as disciplinas e te mostra o relatório. |
| *"Vou viajar de 10/11 a 20/11, quantas faltas ainda posso ter?"* | Ele anota a viagem e calcula quanto sobra em cada disciplina. |
| *"Vou faltar sexta que vem."* | Anota a falta prevista e mostra o impacto. |
| *"Faltei Cálculo hoje."* | Anota a falta. Use isso principalmente nas disciplinas em que o professor não faz chamada no SIGAA. |
| *"Começou o semestre novo, faz o relatório."* | Ele cria o semestre novo e faz tudo de novo. |

Na primeira vez de cada semestre ele precisa entrar no SIGAA. Depois disso, quando você
só avisa uma falta nova, ele refaz a conta sem precisar entrar de novo (a não ser que você
peça um relatório atualizado).

---

## Como a conta é feita

As regras da UFPE (Resolução 04/94 do CCEPE, LDB 9.394/96 e Portaria Normativa 07/2022):

- Cada aula conta como **50 minutos**. Uma disciplina de 60h tem, portanto, **72 aulas**.
- Para passar, você precisa de **pelo menos 75% de presença**. Ou seja, pode faltar até
  **25% das aulas**:

| Carga horária | Aulas no semestre | Máximo de faltas |
|---|---|---|
| 30h | 36 | 9 |
| 45h | 54 | 13 |
| 60h | 72 | 18 |
| 90h | 108 | 27 |

- **Falta conta por aula, não por dia.** Se a disciplina tem 2 horários seguidos, faltar
  esse dia são 2 faltas. Se tem 4 horários, são 4.
- Feriados não contam como falta.

## Seus dados ficam com você

- Tudo o que é seu (disciplinas, faltas, viagens, relatórios) fica numa pasta `dados/`
  **no seu computador**. Essa pasta nunca é enviada para este repositório público.
- Se quiser um backup, dá para guardar a pasta `dados/` num repositório **privado** seu
  no GitHub. É só pedir ao Claude.
- O login no SIGAA é feito **por você**, no navegador. O Claude só lê as páginas depois
  que você entrou.

## Perguntas frequentes

**Isso é oficial da UFPE?**
Não. É uma ferramenta independente, feita por um aluno. O resultado oficial é sempre o do
SIGAA e da coordenação do seu curso. Use como apoio e, na dúvida, confirme com o professor.

**Funciona para qualquer curso?**
Sim, para qualquer curso da UFPE que use o SIGAA, de graduação.

**E em outra universidade que usa SIGAA?**
Provavelmente funciona, mas as regras podem ser diferentes (por exemplo, a duração da
aula). Avise o Claude da sua universidade e das regras de lá.

**O professor não lança a chamada no SIGAA. E agora?**
O SIGAA vai mostrar 100% de presença, mas o professor pode lançar tudo no fim do semestre.
Sempre que faltar nessas disciplinas, diga ao Claude *"faltei [disciplina] hoje"* para ele
manter a conta por você.

**Preciso pagar alguma coisa além do plano do Claude?**
Não.

---

<details>
<summary>Para quem quer mexer nos detalhes técnicos</summary>

```
SKILL.md              instruções que o Claude segue
scripts/faltas.py     faz a conta (Python 3.11+, sem dependências)
modelo-periodo.toml   modelo de arquivo de semestre
exemplo/              exemplo fictício completo
dados/                SEUS dados (fica fora do git)
  periodos/<semestre>.toml          faltas previstas, faltas anotadas, feriados
  periodos/<semestre>.turmas.json   o que foi lido do SIGAA
  relatorios/                       relatórios gerados
```

Para rodar a conta direto no terminal:

```bash
python scripts/faltas.py exemplo/2026.2.toml exemplo/2026.2.turmas.json --hoje 2026-10-06
```

Formato das faltas que você anota (no arquivo do semestre):

```toml
[[ausencias]]          # vale para todas as disciplinas
motivo = "Viagem"
de = "2026-11-10"
ate = "2026-11-20"

[[faltas_manuais]]     # uma disciplina, um dia
disciplina = "cálculo" # código (MAT001) ou parte do nome
data = "2026-09-15"
aulas = 2              # opcional
```

Sugestões e correções são bem-vindas via *issues* e *pull requests*.
</details>

Licença: [MIT](LICENSE).
