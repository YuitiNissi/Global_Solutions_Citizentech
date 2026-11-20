"""Executa a avaliação do assistente e atualiza os relatórios em docs/.

    python src/avaliar.py

Gera duas rodadas com as mesmas perguntas:
- rodada 1 (linha de base): busca original, só com a etapa 1;
- rodada 2 (versão atual): etapa 1 + etapa 2 de correspondência aproximada.
"""

import sys

from modulos import avaliacao, usabilidade
from modulos.assistente import carregar_base


CONJUNTOS = (
    (
        "Conjunto principal",
        avaliacao.ARQUIVO_PERGUNTAS,
        "22 perguntas: diretas, reformuladas, ambíguas, fora do escopo, vazias e com erro de digitação.",
    ),
    (
        "Conjunto de validação",
        avaliacao.ARQUIVO_VALIDACAO,
        "14 perguntas novas, escritas antes da melhoria da busca e nunca usadas para ajustá-la. "
        "Inclui perguntas fora do escopo com palavras do domínio, como merenda e família.",
    ),
)


def avaliar_conjuntos(base, etapa_aproximada=True):
    conjuntos = []
    for rotulo, caminho, descricao in CONJUNTOS:
        perguntas = avaliacao.carregar_perguntas(caminho, base=base)
        linhas = avaliacao.executar_testes(base, perguntas, etapa_aproximada=etapa_aproximada)
        conjuntos.append({
            "nome": rotulo, "descricao": descricao, "linhas": linhas, "resumo": avaliacao.resumir(linhas),
        })
    return conjuntos


def main():
    base = carregar_base()
    linha_de_base = avaliar_conjuntos(base, etapa_aproximada=False)
    avaliacao.gerar_relatorio(
        linha_de_base, None, nome="resultados_rodada1",
        titulo="Rodada 1 · linha de base (busca original, só etapa 1)",
    )

    atual = avaliar_conjuntos(base)
    comparacao = avaliacao.comparar_modelos(base, avaliacao.carregar_perguntas(base=base))
    avaliacao.gerar_relatorio(atual, comparacao, titulo="Rodada 2 · versão atual (etapas 1 e 2)")

    tarefas = usabilidade.executar_roteiro()
    usabilidade.gerar_relatorio(tarefas)

    for rodada, conjuntos in (("Rodada 1", linha_de_base), ("Rodada 2", atual)):
        for conjunto in conjuntos:
            resumo = conjunto["resumo"]
            print(f"{rodada} · {conjunto['nome']}: {resumo['acertos']}/{resumo['total']} · taxa de acerto "
                  f"{resumo['taxa_acerto']:.1f}% · tempo médio {resumo['tempo_medio_ms']:.3f} ms · "
                  f"respostas indevidas {resumo['respostas_indevidas']}")
    for codigo, dados in comparacao.items():
        print(f"Modelo {codigo}: {dados['taxa_geral']:.1f}% dos critérios de resposta atendidos")
    concluidas = sum(item["concluida"] for item in tarefas)
    print(f"Roteiro de facilidade de uso: {concluidas}/{len(tarefas)} tarefas concluídas")
    print("Relatórios em docs/: resultados_testes.md/.csv, resultados_rodada1.md/.csv, resultados_usabilidade.md")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    main()
