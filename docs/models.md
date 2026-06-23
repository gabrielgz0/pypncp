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
| `unidade_nome` | `str \| None` | — |
| `orgao_uf` | `str \| None` | — |
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
| `numero_sequencial` | `str` | Número sequencial |
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
| `situacao` | `str \| None` | Situação do item |
| `tem_resultado` | `bool \| None` | Se possui preço homologado |
| `tipo` | `str \| None` | Tipo do item (material ou serviço) |
| `tipo_nome` | `str \| None` | Nome do tipo |
| `criterio_julgamento_id` | `int \| None` | ID do critério de julgamento |
| `criterio_julgamento_nome` | `str \| None` | Critério de julgamento (Menor Preço, etc.) |
| `situacao_compra_item` | `int \| None` | Código da situação do item |
| `item_categoria_id` | `int \| None` | ID da categoria do item |
| `item_categoria_nome` | `str \| None` | Nome da categoria do item |
| `ncm_nbs_codigo` | `str \| None` | Código NCM/NBS |
| `ncm_nbs_descricao` | `str \| None` | Descrição NCM/NBS |
| `catalogo` | `str \| None` | Catálogo de referência |
| `catalogo_codigo_item` | `str \| None` | Código do item no catálogo |
| `categoria_item_catalogo` | `str \| None` | Categoria no catálogo |
| `incentivo_produtivo_basico` | `bool \| None` | Incentivo produtivo básico |
| `tipo_beneficio` | `int \| None` | Código do tipo de benefício |
| `tipo_beneficio_nome` | `str \| None` | Tipo de benefício |
| `aplicabilidade_margem_preferencia_normal` | `bool \| None` | Aplicabilidade margem preferência normal |
| `aplicabilidade_margem_preferencia_adicional` | `bool \| None` | Aplicabilidade margem preferência adicional |
| `percentual_margem_preferencia_normal` | `str \| None` | Percentual margem preferência normal |
| `percentual_margem_preferencia_adicional` | `str \| None` | Percentual margem preferência adicional |
| `tipo_margem_preferencia` | `str \| None` | Tipo de margem de preferência |
| `exigencia_conteudo_nacional` | `bool \| None` | Exigência de conteúdo nacional |
| `orcamento_sigiloso` | `bool \| None` | Orçamento sigiloso |
| `data_inclusao` | `str \| None` | Data de inclusão |
| `data_atualizacao` | `str \| None` | Data de atualização |
| `informacao_complementar` | `str \| None` | Informação complementar |
| `patrimonio` | `str \| None` | Número do patrimônio |
| `codigo_registro_imobiliario` | `str \| None` | Código do registro imobiliário |
| `imagem` | `int \| None` | Identificador da imagem |

## ResultadoItem

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `fornecedor_nome` | `str` | Nome do fornecedor vencedor |
| `ni_fornecedor` / `cnpj` | `str` | CNPJ do fornecedor |
| `porte_fornecedor_id` | `int \| None` | ID do porte do fornecedor |
| `porte_fornecedor_nome` | `str \| None` | Porte do fornecedor (Demais, ME, EPP, etc.) |
| `natureza_juridica_id` | `str \| None` | Código da natureza jurídica |
| `natureza_juridica_nome` | `str \| None` | Natureza jurídica |
| `tipo_pessoa` | `str \| None` | Tipo de pessoa (PJ, PF) |
| `codigo_pais` | `str \| None` | Código do país |
| `numero_item` | `int \| None` | Número do item no resultado |
| `valor_unitario_homologado` | `float \| None` | Preço unitário homologado |
| `valor_total_homologado` | `float \| None` | Preço total homologado |
| `quantidade_homologada` | `float \| None` | Quantidade homologada |
| `data_resultado` | `str \| None` | Data do resultado |
| `sequencial_resultado` | `int \| None` | Sequencial do resultado |
| `situacao` | `str \| None` | Situação do resultado |
| `percentual_desconto` | `float \| None` | Percentual de desconto |
| `aplicacao_margem_preferencia` | `bool \| None` | Aplicação de margem de preferência |
| `aplicacao_beneficio_me_epp` | `bool \| None` | Benefício ME/EPP aplicado |
| `aplicacao_criterio_desempate` | `bool \| None` | Critério de desempate aplicado |
| `amparo_legal_margem_preferencia` | `str \| None` | Amparo legal margem de preferência |
| `amparo_legal_criterio_desempate` | `str \| None` | Amparo legal critério de desempate |
| `indicador_subcontratacao` | `bool \| None` | Indicador de subcontratação |
| `numero_controle_pncp_compra` | `str \| None` | Número de controle PNCP da compra |
| `situacao_compra_item_resultado_id` | `int \| None` | ID da situação do resultado |
| `ordem_classificacao_srp` | `str \| None` | Ordem de classificação SRP |
| `reserva_remanescente` | `dict \| None` | Reserva remanescente `{codigo, nome}` |
| `data_inclusao` | `str \| None` | Data de inclusão |
| `data_atualizacao` | `str \| None` | Data de atualização |
| `data_cancelamento` | `str \| None` | Data de cancelamento |
| `moeda_estrangeira` | `str \| None` | Moeda estrangeira |
| `valor_nominal_moeda_estrangeira` | `str \| None` | Valor nominal em moeda estrangeira |
| `data_cotacao_moeda_estrangeira` | `str \| None` | Data da cotação da moeda estrangeira |
| `timezone_cotacao_moeda_estrangeira` | `str \| None` | Timezone da cotação |
| `localidade_fornecedor` | `str \| None` | Localidade do fornecedor |
| `localidade_exterior` | `str \| None` | Localidade exterior |
| `pais_origem_produto_servico` | `str \| None` | País de origem do produto/serviço |
| `motivo_cancelamento` | `str \| None` | Motivo do cancelamento |
