"""Calcula quantas faltas ainda cabem em cada disciplina do semestre.

Uso:
    python scripts/faltas.py dados/periodos/2026.2.toml dados/periodos/2026.2.turmas.json [--hoje AAAA-MM-DD]

Imprime um relatório em Markdown. Sem dependências (Python 3.11+).
"""

import argparse
import json
import math
import re
import sys
import tomllib
import unicodedata
from collections import defaultdict
from datetime import date, timedelta

DIAS_SEMANA = {2: "seg", 3: "ter", 4: "qua", 5: "qui", 6: "sex", 7: "sáb"}
MINUTOS_AULA = 50
FREQ_MINIMA = 0.75


def ler_data(texto):
    return date.fromisoformat(str(texto))


def fmt(d):
    return d.strftime("%d/%m")


def aulas_por_dia(horario):
    """'3M56 5M34' -> {weekday_python: n_aulas}. SIGAA: 2=seg ... 7=sáb."""
    por_dia = defaultdict(int)
    for bloco in horario.split():
        m = re.fullmatch(r"(\d+)([MTN])(\d+)", bloco.strip())
        if not m:
            raise ValueError(f"Horário inválido: {bloco!r}")
        dias, _turno, slots = m.groups()
        for d in dias:
            por_dia[int(d) - 2] += len(slots)  # 2 (seg) -> 0 (Monday)
    return dict(por_dia)


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.casefold().strip()


def achar_turma(chave, turmas):
    """Acha a turma pelo código (ex.: MAT001) ou por um trecho do nome (ex.: "cálculo")."""
    k = normalizar(chave)
    achadas = [t for t in turmas if normalizar(t.get("codigo", "")) == k] or               [t for t in turmas if k in normalizar(t["nome"])]
    return achadas[0] if len(achadas) == 1 else None


def datas_entre(inicio, fim):
    d = inicio
    while d <= fim:
        yield d
        d += timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("periodo")
    ap.add_argument("turmas")
    ap.add_argument("--hoje", default=date.today().isoformat())
    args = ap.parse_args()

    with open(args.periodo, "rb") as f:
        periodo = tomllib.load(f)
    with open(args.turmas, encoding="utf-8") as f:
        turmas = json.load(f)["turmas"]

    hoje = ler_data(args.hoje)
    inicio, fim = ler_data(periodo["inicio"]), ler_data(periodo["fim"])
    feriados = {ler_data(x["data"]): x["nome"] for x in periodo.get("feriados", [])}
    incertos = {ler_data(x["data"]): x["nome"] for x in periodo.get("feriados_incertos", [])}

    # data -> motivo de cada dia de ausência prevista
    ausente = {}
    for a in periodo.get("ausencias", []):
        for d in datas_entre(ler_data(a["de"]), ler_data(a["ate"])):
            if inicio <= d <= fim:
                ausente[d] = a.get("motivo", "")

    linhas, alertas, premissas = [], [], []

    # Faltas que o próprio aluno anotou (professor não registra, ou ainda não lançou).
    manuais = defaultdict(list)  # código/nome da turma -> [(data, aulas|None, motivo)]
    for fm in periodo.get("faltas_manuais", []):
        t = achar_turma(fm["disciplina"], turmas)
        if t is None:
            alertas.append(f"❓ Falta manual de {fmt(ler_data(fm['data']))} ignorada: disciplina "
                           f"\"{fm['disciplina']}\" não encontrada (ou ambígua).")
            continue
        manuais[t["nome"]].append((ler_data(fm["data"]), fm.get("aulas"), fm.get("motivo", "")))

    for t in turmas:
        por_dia = aulas_por_dia(t["horario"])
        total = round(t["ch_horas"] * 60 / MINUTOS_AULA)
        limite = total - math.ceil(FREQ_MINIMA * total)
        sem_aula = {ler_data(x) for x in t.get("sem_aula", [])}
        registra = t.get("registra_chamada", True)
        ja_lancadas = {ler_data(x) for x in t.get("datas_faltas_registradas", [])}

        anotadas = []
        for d, aulas, motivo in sorted(manuais[t["nome"]]):
            if d in ja_lancadas:
                premissas.append(f"{t['nome']}: falta manual de {fmt(d)} já está lançada no SIGAA (não contada duas vezes).")
                continue
            n = aulas if aulas is not None else por_dia.get(d.weekday(), 0)
            if not n:
                alertas.append(f"❓ **{t['nome']}**: falta manual de {fmt(d)} ignorada — não há aula nesse dia "
                               f"da semana (informe `aulas = N` se foi uma aula extra).")
                continue
            anotadas.append((d, n))
        datas_anotadas = {d for d, _ in anotadas}

        previstas, extras_pior = [], []
        for d in sorted(ausente):
            n = por_dia.get(d.weekday(), 0)
            # Ausências passadas já aparecem nas faltas lançadas, exceto se o professor não registra.
            if not n or (d < hoje and registra) or d in feriados or d in datas_anotadas:
                continue
            if d in sem_aula or d in incertos:
                extras_pior.append((d, n))
            else:
                previstas.append((d, n))

        lancadas = t.get("faltas_registradas", 0) + sum(n for _, n in anotadas)
        n_prev = sum(n for _, n in previstas)
        n_pior = n_prev + sum(n for _, n in extras_pior)
        sobra = limite - lancadas - n_prev
        sobra_pior = limite - lancadas - n_pior
        maior_dia = max(por_dia.values())
        dias_sobra = max(sobra, 0) // maior_dia
        aprox = "≈" if len(set(por_dia.values())) > 1 else ""

        nome = t["nome"]
        datas_txt = ", ".join(fmt(d) for d, _ in previstas) or "—"
        n_anot = sum(n for _, n in anotadas)
        lancadas_txt = str(t.get("faltas_registradas", 0))
        if anotadas:
            lancadas_txt += f" + {n_anot} anotadas ({', '.join(fmt(d) for d, _ in anotadas)})"
        sobra_txt = f"**{sobra} aulas** ({aprox}{dias_sobra} dia{'s' if dias_sobra != 1 else ''})"
        if sobra_pior != sobra:
            sobra_txt += f"<br>pior caso: {sobra_pior}"
        linhas.append(
            f"| {nome} | {'✅' if registra else '❌ não registra'} | "
            f"{'✅' if t.get('tem_plano', True) else '❌ sem plano'} | {lancadas_txt} | "
            f"{n_prev} ({datas_txt}) | {lancadas + n_prev} / {limite} | {sobra_txt} |"
        )

        if sobra < 0:
            alertas.append(f"🔴 **{nome}**: reprova por falta com as ausências previstas ({lancadas + n_prev} > {limite}).")
        elif sobra == 0:
            alertas.append(f"🔴 **{nome}**: você fica exatamente no limite — qualquer falta a mais reprova.")
        elif dias_sobra == 0:
            alertas.append(f"🟠 **{nome}**: sobram só {sobra} aula(s) — não dá para faltar mais nenhum dia inteiro.")
        if not registra:
            alertas.append(f"⚪ **{nome}**: o professor não registra chamada no SIGAA (pode lançar tudo no fim do semestre).")
        if not t.get("tem_plano", True):
            alertas.append(f"⚪ **{nome}**: não tem Plano de Curso cadastrado.")
        for ev in t.get("eventos", []):
            d = ler_data(ev["data"])
            if d in ausente and d >= hoje:
                alertas.append(f"📌 **{nome}**: {fmt(d)} — {ev['descricao']} (você estará ausente: {ausente[d]}).")
        for d, n in extras_pior:
            motivo = incertos.get(d) or "não aparece no cronograma"
            premissas.append(f"{nome}: {fmt(d)} não contado ({motivo}); se houver aula, +{n} falta(s).")

    print(f"# Relatório de faltas — {periodo['semestre']} (gerado em {hoje.strftime('%d/%m/%Y')})\n")
    if ausente:
        print("**Ausências previstas:** " + "; ".join(
            f"{a.get('motivo', '')} {fmt(ler_data(a['de']))}–{fmt(ler_data(a['ate']))}"
            for a in periodo["ausencias"]) + "\n")
    print("| Disciplina | Chamada | Plano | Faltas já tidas (SIGAA + anotadas) | Faltas previstas (datas) | Total / limite | Ainda pode faltar |")
    print("|---|---|---|---|---|---|---|")
    print("\n".join(linhas))
    if alertas:
        print("\n## Alertas\n")
        print("\n".join(f"- {a}" for a in alertas))
    print("\n## Premissas\n")
    print("- Aula = 50 min; limite = 25% das aulas da CH (60h → 18 faltas; 45h → 13).")
    print("- \"Dias\" = dias de aula inteiros que ainda cabem (no dia com mais horários).")
    for d, nome in sorted(feriados.items()):
        print(f"- {fmt(d)} ({nome}) tratado como feriado.")
    for p in premissas:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
