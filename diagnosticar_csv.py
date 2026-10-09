import pandas as pd


SCHEMA_PROPOSICOES = [
    {"name": "ano", "type": "STRING"},
    {"name": "id", "type": "INT64"},
    {"name": "descricaoTipo", "type": "STRING"},
    {"name": "ementa", "type": "STRING"},
    {"name": "ementaDetalhada", "type": "STRING"},
    {"name": "dataApresentacao", "type": "DATE"},
    {"name": "ultimoStatus_dataHora", "type": "TIMESTAMP"},
    {"name": "ultimoStatus_sequencia", "type": "INT64"},
    {"name": "ultimoStatus_descricaoTramitacao", "type": "STRING"},
    {"name": "ultimoStatus_idTipoTramitacao", "type": "INT64"},
    {"name": "ultimoStatus_descricaoSituacao", "type": "STRING"},
    {"name": "ultimoStatus_apreciacao", "type": "STRING"},
]


def diagnosticar(caminho):

    df = pd.read_csv(caminho, sep=";")

    print("\n" + "=" * 80)
    print("DIAGNÓSTICO - PROPOSIÇÕES")
    print("=" * 80)

    for campo in SCHEMA_PROPOSICOES:

        coluna = campo["name"]
        esperado = campo["type"]

        if coluna not in df.columns:
            print(f"❌ {coluna}")
            print(f"   Pandas: COLUNA NÃO ENCONTRADA")
            print(f"   BigQuery: {esperado}")
            continue

        dtype = str(df[coluna].dtype)

        print(f"{coluna}")
        print(f"   Pandas:    {dtype}")
        print(f"   BigQuery:  {esperado}")

        # Verifica compatibilidade básica
        if esperado == "STR":
            compativel = dtype in ["object", "string"]

        elif esperado == "INT64":
            compativel = dtype in ["int64", "Int64"]

        elif esperado == "DATE":
            compativel = "datetime" in dtype

        elif esperado == "TIMESTAMP":
            compativel = "datetime" in dtype

        else:
            compativel = True

        if compativel:
            print("   Status:    OK")
        else:
            print("   Status:    ⚠️ INCOMPATÍVEL")

        print()


if __name__ == "__main__":

    caminho = "C:/prefect/data/camara_leg_csv/proposicoes-2024.csv"

    diagnosticar(caminho)
