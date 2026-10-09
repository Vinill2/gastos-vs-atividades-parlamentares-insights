TRANSFORM_PROPOSICOES = [
    (
        "selecionar",
        [
            "ano",
            "id",
            "descricaoTipo",
            "ementa",
            "ementaDetalhada",
            "dataApresentacao",
            "ultimoStatus_dataHora",
            "ultimoStatus_sequencia",
            "ultimoStatus_descricaoTramitacao",
            "ultimoStatus_idTipoTramitacao",
            "ultimoStatus_descricaoSituacao",
            "ultimoStatus_apreciacao",
        ],
    ),
    (
        "converter_data",
        ["dataApresentacao",],
    ),
    (
        "converter_datetime",
        ["ultimoStatus_dataHora"],
    ),
]


TRANSFORM_PROPOSICOES_AUTORES = [
    (
        "selecionar",
        [
            "idProposicao",
            "tipoAutor",
            "nomeAutor",
            "idDeputadoAutor",
            "siglaPartidoAutor",
            "siglaUFAutor",
        ],
    ),
]


TRANSFORM_GASTOS_PARLAMENTARES = [
    (
        "selecionar_existentes",
        [
            "numAno",
            "ideCadastro",
            "txtDescricao",
            "txtFornecedor",
            "datEmissao",
            "vlrLiquido",
        ],
    ),
    (
        "converter_numero",
        ["ideCadastro","numAno"],
    ),
    (
        "converter_datetime",
        ["datEmissao"],
    ),
    (
        "normalizar_nulos",
        [
            "txtDescricao",
            "txtFornecedor",
        ],
    ),
    (
        "converter_decimal",
        ["vlrLiquido"],
    ),
]


TRANSFORM_DEPUTADOS = [
    (
        "selecionar",
        [
            "uri",
            "nome",
            "siglaSexo",
            "dataNascimento",
        ],
    ),
    (
        "extrair_id",
        {
            "origem": "uri",
            "destino": "id",
        },
    ),
]