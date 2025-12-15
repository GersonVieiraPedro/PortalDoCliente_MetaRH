"""
Script para converter o arquivo CSV TB_Duplicata em comandos INSERT SQL
Gera um arquivo .sql com todos os comandos INSERT individuais
"""

import csv
import os
from datetime import datetime

# Configurações
CSV_FILE = '20230620061719_TB_Duplicata.csv'
OUTPUT_SQL = 'insert_tb_duplicata.sql'
BATCH_SIZE = 1000  # Número de INSERTs por transação

def format_value(value, column_name):
    """Formata o valor de acordo com o tipo de dado"""
    # Remove aspas extras se houver
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    # Valores vazios ou nulos
    if value == '' or value.upper() == 'NULL':
        return 'NULL'

    # Booleanos
    if column_name in ['InclusaoOK', 'NF13oSalario', 'FlagExportacao', 'ProvisaoIntegrada',
                       'BaixaIntegrada', 'NfeExportada', 'Tri_Tri', 'ContratoMulti',
                       'LiqNFe', 'APISinc', 'APISincExterno']:
        if value.upper() in ['TRUE', '1', 'T', 'Y', 'YES']:
            return '1'
        elif value.upper() in ['FALSE', '0', 'F', 'N', 'NO']:
            return '0'
        else:
            return 'NULL'

    # Números (INT)
    if column_name in ['CodigoEmpresaFat', 'CodigoFilialFat', 'Duplicata', 'CodigoEmpresa',
                       'CodigoFilial', 'CodigoCliente', 'CodigoContrato', 'TipoFat',
                       'CodigoCentroCusto', 'CodigoVendedor', 'CodigoSelecionador',
                       'CodigoRecrutador', 'CodigoBanco', 'ChaveMovtoBanco', 'ChaveMovtoBancoJD',
                       'CodigoBancoOriginal', 'NroNFe', 'NumeroRPS', 'NroNotaDB', 'NossoNumero',
                       'Situacao', 'CodigoCR', 'CodigoCRJD', 'FaseEnvioCobr', 'TipoBaixaRemessa',
                       'QtdParcelas']:
        try:
            # Remove espaços e converte
            clean_value = value.strip()
            if clean_value:
                return str(int(float(clean_value)))
            return 'NULL'
        except (ValueError, TypeError):
            return 'NULL'

    # Números decimais (DECIMAL)
    if 'Valor' in column_name or 'Base' in column_name or 'Alq' in column_name:
        try:
            clean_value = value.strip()
            if clean_value:
                return str(float(clean_value))
            return 'NULL'
        except (ValueError, TypeError):
            return 'NULL'

    # Datas
    if 'Data' in column_name and column_name not in ['DataCompetencia', 'DataCompetencia2']:
        if value and value != '':
            try:
                # Tenta parsear a data
                # Formato esperado: 2000-01-11 00:00:00.0000000
                date_str = value.strip()
                if date_str:
                    # Remove os milissegundos extras
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    return f"'{date_str}'"
                return 'NULL'
            except:
                return 'NULL'
        return 'NULL'

    # Strings (escapa aspas simples)
    value = value.replace("'", "''")
    return f"'{value}'"

def generate_insert_statements():
    """Gera os comandos INSERT SQL a partir do CSV"""

    print(f"Lendo arquivo CSV: {CSV_FILE}")

    # Verifica se o arquivo existe
    if not os.path.exists(CSV_FILE):
        print(f"ERRO: Arquivo {CSV_FILE} não encontrado!")
        return

    # Abre o arquivo de saída
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as sql_file:
        # Cabeçalho do SQL
        sql_file.write("-- ========================================\n")
        sql_file.write("-- Script: INSERT de dados na TB_Duplicata\n")
        sql_file.write(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sql_file.write(f"-- Origem: {CSV_FILE}\n")
        sql_file.write("-- ========================================\n\n")
        sql_file.write("USE [NomeDoBanco]; -- ALTERE PARA O NOME DO SEU BANCO DE DADOS\n")
        sql_file.write("GO\n\n")
        sql_file.write("SET NOCOUNT ON;\n")
        sql_file.write("GO\n\n")

        # Lê o CSV
        with open(CSV_FILE, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter='|')

            # Pega os nomes das colunas
            columns = reader.fieldnames
            columns_str = ', '.join(columns)

            print(f"Colunas encontradas: {len(columns)}")
            print("Gerando comandos INSERT...")

            count = 0
            batch_count = 0

            # Inicia primeira transação
            sql_file.write("BEGIN TRANSACTION;\n")
            sql_file.write("PRINT 'Inserindo lote 1...';\n\n")

            for row in reader:
                count += 1

                # Formata os valores
                values = []
                for col in columns:
                    value = row[col]
                    formatted = format_value(value, col)
                    values.append(formatted)

                values_str = ', '.join(values)

                # Gera o INSERT
                sql_file.write(f"INSERT INTO dbo.TB_Duplicata ({columns_str})\n")
                sql_file.write(f"VALUES ({values_str});\n\n")

                # A cada BATCH_SIZE registros, faz COMMIT e inicia nova transação
                if count % BATCH_SIZE == 0:
                    batch_count += 1
                    sql_file.write("COMMIT TRANSACTION;\n")
                    sql_file.write(f"PRINT 'Lote {batch_count} concluído. Total: {count} registros.';\n")
                    sql_file.write("GO\n\n")
                    sql_file.write("BEGIN TRANSACTION;\n")
                    sql_file.write(f"PRINT 'Inserindo lote {batch_count + 1}...';\n\n")

                # Progresso no console
                if count % 5000 == 0:
                    print(f"Processados {count} registros...")

            # Commit final
            sql_file.write("COMMIT TRANSACTION;\n")
            sql_file.write(f"PRINT 'Importação concluída! Total: {count} registros.';\n")
            sql_file.write("GO\n\n")

            # Estatísticas finais
            sql_file.write("-- Verificação\n")
            sql_file.write("SELECT COUNT(*) AS TotalRegistros FROM dbo.TB_Duplicata;\n")
            sql_file.write("GO\n")

            print(f"\nConcluído!")
            print(f"Total de registros processados: {count}")
            print(f"Arquivo SQL gerado: {OUTPUT_SQL}")
            print(f"Tamanho estimado: {os.path.getsize(OUTPUT_SQL) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    try:
        generate_insert_statements()
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
