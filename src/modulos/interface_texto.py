"""Interface textual do assistente. Entrada e saída são injetáveis para permitir testes roteirizados."""

from modulos.assistente import (
    ARQUIVO_BASE,
    ErroBase,
    buscar,
    buscar_por_id,
    carregar_base,
    indexar_por_id,
    organizar_por_tema,
    relacionados,
    validado,
)
from modulos.modelos_resposta import (
    MODELO_PADRAO,
    MODELOS,
    formatar_orientacao,
    formatar_resultado,
    nota_aproximada,
)


LINHA = "=" * 66
CABECALHO = f"""{LINHA}
 HORTA VIVA · Citizen Assist AI · HortaTeam
 Orientações comunitárias sobre alimentação e hortas escolares
 Protótipo acadêmico (FIAP · Global Solution 2026.2). Não é canal
 oficial de órgãos públicos e não pede dados pessoais.
{LINHA}"""
VOLTAR = "(Enter volta ao menu)"


def _menu(modelo):
    return "\n".join([
        "",
        "MENU PRINCIPAL",
        "  1. Fazer uma pergunta",
        "  2. Explorar por tema",
        "  3. Consultar por identificador",
        f"  4. Trocar modelo de resposta (atual: {MODELOS[modelo].nome})",
        "  5. Executar as perguntas de teste e ver indicadores",
        "  0. Sair",
    ])


class Sessao:
    def __init__(self, base, entrada, saida):
        self.base = base
        self.indice = indexar_por_id(base)
        self.temas = organizar_por_tema(base)
        self.entrada = entrada
        self.saida = saida
        self.modelo = MODELO_PADRAO

    def escolher(self, quantidade, rotulo):
        """Lê um número de 1 a quantidade. Retorna o índice escolhido ou None (Enter)."""
        while True:
            texto = self.entrada(rotulo).strip()
            if not texto:
                return None
            if texto.isdigit() and 1 <= int(texto) <= quantidade:
                return int(texto) - 1
            self.saida(f"Opção inexistente. Digite um número de 1 a {quantidade} ou Enter para voltar.")

    def mostrar_orientacao(self, registro):
        """Exibe a orientação e permite seguir pelo grafo de assuntos relacionados."""
        trilha = []
        while registro is not None:
            trilha.append(registro["subtema"])
            vizinhos = relacionados(registro, self.indice) if self.modelo == "B" else []
            self.saida("")
            self.saida(formatar_orientacao(registro, self.modelo, vizinhos))
            if len(trilha) > 1:
                self.saida("Caminho: " + " > ".join(trilha))
            if not vizinhos:
                return
            escolha = self.escolher(len(vizinhos), f"Número do assunto relacionado {VOLTAR}: ")
            registro = vizinhos[escolha] if escolha is not None else None

    def tratar(self, resultado):
        if resultado.status == "encontrada":
            if resultado.aproximada and self.modelo == "B":
                self.saida(nota_aproximada(resultado.registros[0]))
            self.mostrar_orientacao(resultado.registros[0])
            return
        self.saida(formatar_resultado(resultado, self.modelo))
        opcoes = resultado.registros if resultado.status == "ambigua" else resultado.sugestoes
        if self.modelo == "B" and opcoes:
            escolha = self.escolher(len(opcoes), f"Número do assunto {VOLTAR}: ")
            if escolha is not None:
                self.mostrar_orientacao(opcoes[escolha])

    def perguntar(self):
        self.saida("Escreva sua dúvida em poucas palavras. Não digite dados pessoais.")
        self.tratar(buscar(self.entrada("Sua pergunta: "), self.base))

    def explorar(self):
        temas = list(self.temas)
        self.saida("\nTemas disponíveis:")
        for numero, tema in enumerate(temas, start=1):
            self.saida(f"  {numero}. {tema} ({len(self.temas[tema])} assuntos)")
        escolha = self.escolher(len(temas), f"Número do tema {VOLTAR}: ")
        if escolha is None:
            return
        tema = temas[escolha]
        subtemas = list(self.temas[tema])
        self.saida(f"\nAssuntos de {tema}:")
        for numero, subtema in enumerate(subtemas, start=1):
            identificadores = ", ".join(item["id"] for item in self.temas[tema][subtema])
            self.saida(f"  {numero}. {subtema} ({identificadores})")
        escolha = self.escolher(len(subtemas), f"Número do assunto {VOLTAR}: ")
        if escolha is None:
            return
        registros = [item for item in self.temas[tema][subtemas[escolha]] if validado(item)]
        if not registros:
            self.saida("Orientação pendente de validação. Escolha outro assunto.")
            return
        self.mostrar_orientacao(registros[0])

    def consultar_id(self):
        self.saida("Identificadores seguem o formato tema-número: alimentacao-01, cultivo-02, escola-03.")
        self.tratar(buscar_por_id(self.entrada("Identificador: "), self.base))

    def trocar_modelo(self):
        self.modelo = "A" if self.modelo == "B" else "B"
        self.saida(f"Modelo de resposta: {MODELOS[self.modelo].nome}.")
        self.saida(f"Instrução: {MODELOS[self.modelo].instrucao}")

    def indicadores(self):
        from modulos.avaliacao import carregar_perguntas, executar_testes, resumir

        linhas = executar_testes(self.base, carregar_perguntas(base=self.base), repeticoes=20)
        resumo = resumir(linhas)
        self.saida(f"\nPerguntas de teste: {resumo['total']}")
        self.saida(f"Acertos: {resumo['acertos']} · taxa de acerto: {resumo['taxa_acerto']:.1f}%")
        self.saida(f"Tempo médio de consulta: {resumo['tempo_medio_ms']:.2f} ms")
        for tipo, (acertos, total) in resumo["por_tipo"].items():
            self.saida(f"  {tipo}: {acertos}/{total}")
        self.saida("Relatório completo: execute python src/avaliar.py e abra docs/resultados_testes.md")


def executar(entrada=input, saida=print, caminho_base=ARQUIVO_BASE):
    saida(CABECALHO)
    try:
        base = carregar_base(caminho_base)
    except ErroBase as erro:
        saida(f"Erro: {erro}")
        saida("Corrija o arquivo data/conhecimento.json e execute o programa novamente.")
        return 1

    sessao = Sessao(base, entrada, saida)
    saida(f"Base carregada: {len(base)} orientações em {len(sessao.temas)} temas: " + "; ".join(sessao.temas) + ".")
    acoes = {
        "1": sessao.perguntar,
        "2": sessao.explorar,
        "3": sessao.consultar_id,
        "4": sessao.trocar_modelo,
        "5": sessao.indicadores,
    }
    try:
        while True:
            saida(_menu(sessao.modelo))
            opcao = entrada("Escolha uma opção: ").strip()
            if opcao == "0":
                break
            if not opcao:
                saida("Entrada vazia. Digite o número de uma opção do menu.")
            elif opcao not in acoes:
                saida("Opção inexistente. Digite um número de 0 a 5.")
            else:
                acoes[opcao]()
    except (EOFError, KeyboardInterrupt):
        saida("")
    saida("Até logo! Lembre-se de confirmar as orientações nas fontes indicadas.")
    return 0
