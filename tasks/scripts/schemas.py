SCHEMA_PROPOSICOES = [
    {"name": "ano", "type": "INT64"},
    {"name": "id", "type": "INT64"},
    {"name": "descricaoTipo", "type": "STRING"},
    {"name": "ementa", "type": "STRING"},
    {"name": "ementaDetalhada", "type": "STRING"},
    {"name": "dataApresentacao", "type": "DATE"},
    {"name": "ultimoStatus_dataHora", "type": "TIMESTAMP"},
    {"name": "ultimoStatus_sequencia", "type": "STRING"},
    {"name": "ultimoStatus_descricaoTramitacao", "type": "STRING"},
    {"name": "ultimoStatus_idTipoTramitacao", "type": "INT64"},
    {"name": "ultimoStatus_descricaoSituacao", "type": "STRING"},
    {"name": "ultimoStatus_apreciacao", "type": "STRING"},
]


SCHEMA_PROPOSICOES_AUTORES = [
    {"name": "idProposicao", "type": "INT64"},
    {"name": "tipoAutor", "type": "STRING"},
    {"name": "nomeAutor", "type": "STRING"},
    {"name": "idDeputadoAutor", "type": "INT64"},
    {"name": "siglaPartidoAutor", "type": "STRING"},
    {"name": "siglaUFAutor", "type": "STRING"},
]


SCHEMA_GASTOS_PARLAMENTARES = [
    {"name": "numAno", "type": "INT64"},
    {"name": "ideCadastro", "type": "INT64"},
    {"name": "txtDescricao", "type": "STRING"},
    {"name": "txtFornecedor", "type": "STRING"},
    {"name": "datEmissao", "type": "DATE"},
    {"name": "vlrLiquido", "type": "NUMERIC"},
]


SCHEMA_DEPUTADOS = [
    {"name": "uri", "type": "STRING"},
    {"name": "nome", "type": "STRING"},
    {"name": "siglaSexo", "type": "STRING"},
    {"name": "dataNascimento", "type": "DATE"},
    {"name": "id", "type": "INT64"},
]