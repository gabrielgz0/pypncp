# Modelos

## Contrato

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_contrato_empenho` | `str` | `numeroContratoEmpenho` |
| `ano_contrato` | `int` | `anoContrato` |
| `sequencial_contrato` | `int` | `sequencialContrato` |
| `objeto_contrato` | `str` | `objetoContrato` |
| `processo` | `str \| None` | `processo` |
| `orgao_cnpj` | `str \| None` | `orgaoEntidade.cnpj` |
| `orgao_nome` | `str \| None` | `orgaoEntidade.razaoSocial` |
| `orgao_uf` | `str \| None` | `unidadeOrgao.ufSigla` |
| `fornecedor_nome` | `str \| None` | `nomeRazaoSocialFornecedor` |
| `ni_fornecedor` | `str \| None` | `niFornecedor` |
| `valor_inicial` | `float \| None` | `valorInicial` |
| `valor_global` | `float \| None` | `valorGlobal` |
| `data_assinatura` | `date \| None` | `dataAssinatura` |
| `data_vigencia_inicio` | `date \| None` | `dataVigenciaInicio` |
| `data_vigencia_fim` | `date \| None` | `dataVigenciaFim` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |
| `numero_controle_pncp` | `str \| None` | `numeroControlePncp` |
| `numero_controle_pncp_compra` | `str \| None` | `numeroControlePncpCompra` |
| `numero_controle_pncp_ata` | `str \| None` | `numeroControlePncpAta` |
| `informacao_complementar` | `str \| None` | `informacaoComplementar` |
| `data_atualizacao_global` | `datetime \| None` | `dataAtualizacaoGlobal` |

## Contratacao

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_compra` | `str` | `numeroCompra` |
| `ano_compra` | `int` | `anoCompra` |
| `sequencial_compra` | `int` | `sequencialCompra` |
| `objeto_compra` | `str` | `objetoCompra` |
| `orgao_cnpj` | `str \| None` | `orgaoEntidade.cnpj` |
| `orgao_nome` | `str \| None` | `orgaoEntidade.razaoSocial` |
| `orgao_uf` | `str \| None` | `unidadeOrgao.ufSigla` |
| `modalidade_nome` | `str \| None` | `modalidadeNome` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |
| `data_abertura_proposta` | `datetime \| None` | `dataAberturaProposta` |
| `valor_total_estimado` | `float \| None` | `valorTotalEstimado` |
| `valor_total_homologado` | `float \| None` | `valorTotalHomologado` |
| `srp` | `bool \| None` | `srp` |
| `modalidade_id` | `int \| None` | `modalidadeId` |
| `data_atualizacao_global` | `datetime \| None` | `dataAtualizacaoGlobal` |

## Ata

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_ata_registro_preco` | `str` | `numeroAtaRegistroPreco` |
| `ano_ata` | `int` | `anoAta` |
| `objeto_contratacao` | `str` | `objetoContratacao` |
| `orgao_cnpj` | `str \| None` | `cnpjOrgao` |
| `orgao_nome` | `str \| None` | `nomeOrgao` |
| `vigencia_inicio` | `datetime \| None` | `vigenciaInicio` |
| `vigencia_fim` | `datetime \| None` | `vigenciaFim` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |
| `cancelado` | `bool \| None` | `cancelado` |
| `possibilidade_adesao` | `bool \| None` | `possibilidadeAdesao` |
| `numero_controle_pncp_ata` | `str \| None` | `numeroControlePncpAta` |
| `numero_controle_pncp_compra` | `str \| None` | `numeroControlePncpCompra` |
| `situacao` | `str \| None` | `situacao` |
| `unidade_nome` | `str \| None` | `unidadeNome` |
| `orgao_uf` | `str \| None` | `ufSigla` |
| `data_atualizacao_global` | `datetime \| None` | `dataAtualizacaoGlobal` |

## SearchResult

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `title` | `str` | Título do documento |
| `description` | `str` | Descrição / objeto |
| `document_type` | `str` | Tipo: `edital`, `contrato`, `ata` |
| `orgao_nome` | `str \| None` | Nome do órgão |
| `orgao_cnpj` | `str \| None` | CNPJ do órgão |
| `uf` | `str \| None` | Unidade federativa |
| `municipio_nome` | `str \| None` | Município |
| `modalidade_licitacao_nome` | `str \| None` | Modalidade (Pregão, Dispensa, etc.) |
| `situacao_nome` | `str \| None` | Situação do documento |
| `valor_global` | `float \| None` | Valor global |
| `data_publicacao_pncp` | `datetime \| None` | Data de publicação |
| `data_assinatura` | `datetime \| None` | Data de assinatura |
| `data_inicio_vigencia` | `datetime \| None` | Início da vigência |
| `data_fim_vigencia` | `datetime \| None` | Fim da vigência |
| `cancelado` | `bool \| None` | Se foi cancelado |
| `tem_resultado` | `bool \| None` | Se tem resultado homologado |
| `esfera_nome` | `str \| None` | Esfera (Federal, Estadual, Municipal) |
| `poder_nome` | `str \| None` | Poder (Executivo, Legislativo, Judiciário) |
| `id` | `str \| None` | Identificador único |
| `numero_controle_pncp` | `str \| None` | Número de controle PNCP |
| `numero_sequencial` | `int \| None` | Número sequencial |
| `tipo_nome` | `str \| None` | Nome do tipo |
| `tipo_contrato_nome` | `str \| None` | Nome do tipo de contrato |
| `exigencia_conteudo_nacional` | `bool \| None` | Exigência de conteúdo nacional |

## ItemCompra

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `numero_item` | `int` | Número do item na compra |
| `descricao` | `str` | Descrição do item |
| `quantidade` | `float` | Quantidade |
| `unidade_medida` | `str \| None` | Unidade (Unitário, Lote, etc.) |
| `valor_unitario_estimado` | `float \| None` | Valor unitário estimado |
| `valor_total` | `float \| None` | Valor total estimado |
| `situacao` | `str \| None` | Situação (Homologado, etc.) |
| `tem_resultado` | `bool \| None` | Se possui preço homologado |
| `tipo` | `str \| None` | Tipo do item |
| `tipo_nome` | `str \| None` | Nome do tipo |

## ResultadoItem

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `fornecedor_nome` | `str` | Nome do fornecedor vencedor |
| `ni_fornecedor` / `cnpj` | `str` | CNPJ do fornecedor |
| `valor_unitario_homologado` | `float \| None` | Preço unitário homologado |
| `valor_total_homologado` | `float \| None` | Preço total homologado |
| `quantidade_homologada` | `float \| None` | Quantidade homologada |
| `data_resultado` | `str \| None` | Data do resultado |
| `sequencial_resultado` | `int \| None` | Sequencial do resultado |
| `situacao` | `str \| None` | Situação do resultado |
