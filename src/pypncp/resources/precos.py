"""Recurso de precos homologados — Integration API do PNCP.

Endpoints nao documentados oficialmente (integram o portal):
    GET /api/pncp/v1/orgaos/{orgao}/compras/{ano}/{compra}/itens
    GET /api/pncp/v1/orgaos/{orgao}/compras/{ano}/{compra}/itens/{item}/resultados

Fluxo completo:
    search (catalogo) → itens da compra → resultados (fornecedor + preco)
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from pypncp._internal.http import HttpClient
from pypncp.models import ItemCompra, ResultadoItem
from pypncp.resources.search import SearchResource


class PrecosResource:
    """Recurso para precos homologados no PNCP.

    Fornece acesso aos precos efetivamente pagos pela administracao
    publica, com fornecedor, CNPJ e data de homologacao.

    Uso:
        async with PNCPClient() as client:
            # Itens de uma compra
            itens = await client.precos.get_items(
                orgao="78680337000770", ano=2024, compra=128
            )
            for item in itens:
                print(item.descricao, item.valor_unitario_estimado)

            # Resultados (precos homologados) de um item
            resultados = await client.precos.get_resultados(
                orgao="78680337000770", ano=2024, compra=128, item=1
            )
            for r in resultados:
                print(r.fornecedor_nome, r.cnpj, r.valor_unitario_homologado)

            # Pipeline completo: busca → precos homologados
            async for preco in client.precos.buscar_precos(
                q="dipirona", tipos_documento="edital", uf="SP"
            ):
                print(preco)
    """

    BASE_URL = "https://pncp.gov.br/api/pncp/v1"

    def __init__(self) -> None:
        self._http = HttpClient(base_url=self.BASE_URL)
        self._search = SearchResource()

    # ------------------------------------------------------------------ #
    #  Itens de uma compra
    # ------------------------------------------------------------------ #

    async def get_items(
        self,
        orgao: str,
        ano: int,
        compra: int,
        pagina: int = 1,
        tamanho_pagina: int = 50,
    ) -> list[ItemCompra]:
        """Retorna os itens de uma compra/contrato.

        Args:
            orgao: CNPJ do orgao (apenas digitos).
            ano: Ano da compra.
            compra: Numero sequencial da compra.
            pagina: Pagina de itens.
            tamanho_pagina: Itens por pagina.
        """
        data = await self._http.get(
            f"/orgaos/{orgao}/compras/{ano}/{compra}/itens",
            params={"pagina": pagina, "tamanhoPagina": tamanho_pagina},
        )
        if isinstance(data, list):
            return [ItemCompra(**item) for item in data]
        return []

    # ------------------------------------------------------------------ #
    #  Resultados de um item (precos homologados)
    # ------------------------------------------------------------------ #

    async def get_resultados(
        self,
        orgao: str,
        ano: int,
        compra: int,
        item: int,
    ) -> list[ResultadoItem]:
        """Retorna os precos homologados de um item.

        Args:
            orgao: CNPJ do orgao.
            ano: Ano da compra.
            compra: Numero sequencial da compra.
            item: Numero do item.
        """
        data = await self._http.get(
            f"/orgaos/{orgao}/compras/{ano}/{compra}/itens/{item}/resultados",
        )
        if isinstance(data, list):
            return [ResultadoItem(**r) for r in data]
        return []

    # ------------------------------------------------------------------ #
    #  Pipeline completo: busca → precos homologados
    # ------------------------------------------------------------------ #

    async def buscar_precos(
        self,
        *,
        q: str,
        tipos_documento: str = "edital",
        ano: int | None = None,
        ordenacao: str | None = "-data",
        status: str | None = "encerradas",
        uf: str | None = None,
        tam_pagina_search: int = 50,
        max_compras: int = 20,
        paginas_itens: int = 3,
    ) -> AsyncIterator[dict[str, Any]]:
        """Pipeline completo: busca no catalogo → itens → precos homologados.

        Para cada compra encontrada, busca os itens e seus resultados.
        Retorna um dict combinado com dados do item + resultado + compra.

        Args:
            q: Termo de busca.
            tipos_documento: Tipo de documento (padrao \"edital\").
            ano: Filtrar por ano (opcional).
            ordenacao: Ordenacao dos resultados.
            status: Status das compras (padrao \"encerradas\").
            uf: Filtrar por UF.
            tam_pagina_search: Itens por pagina na busca.
            max_compras: Maximo de compras a processar.
            paginas_itens: Paginas de itens por compra.
        """
        seen = set()
        pagina = 1
        compras_processadas = 0

        while compras_processadas < max_compras:
            page = await self._search.search(
                q=q,
                tipos_documento=tipos_documento,
                pagina=pagina,
                tam_pagina=tam_pagina_search,
                ordenacao=ordenacao,
                status=status,
                uf=uf,
            )

            if not page.data:
                break

            for result in page.data:
                if compras_processadas >= max_compras:
                    break

                # Extrai orgao, ano, compra do item_url
                # Formato: /compras/{orgao}/{ano}/{compra}
                parts = result.item_url.split("/")
                if len(parts) < 5:
                    continue

                _, _, ni_orgao, str_ano, ni_compra = parts[:5]
                if ano is not None and str_ano != str(ano):
                    continue

                chave = (ni_orgao, ni_compra)
                if chave in seen:
                    continue
                seen.add(chave)

                # Busca itens da compra
                for p in range(1, paginas_itens + 1):
                    itens = await self.get_items(
                        orgao=ni_orgao,
                        ano=int(str_ano),
                        compra=int(ni_compra),
                        pagina=p,
                    )
                    for item in itens:
                        if not item.tem_resultado:
                            continue

                        # Busca resultados/precos deste item
                        resultados = await self.get_resultados(
                            orgao=ni_orgao,
                            ano=int(str_ano),
                            compra=int(ni_compra),
                            item=item.numero_item,
                        )
                        for res in resultados:
                            yield {
                                "descricao": item.descricao,
                                "fornecedor": res.fornecedor_nome,
                                "cnpj": res.ni_fornecedor,
                                "valor_unitario": res.valor_unitario_homologado,
                                "valor_total": res.valor_total_homologado,
                                "quantidade": res.quantidade_homologada,
                                "data": res.data_resultado,
                                "orgao": ni_orgao,
                                "orgao_nome": result.orgao_nome,
                                "link": (
                                    f"https://pncp.gov.br/app/editais"
                                    f"/{ni_orgao}/{str_ano}/{ni_compra}"
                                ),
                            }

                    if len(itens) < tam_pagina_search:
                        break  # nao ha mais paginas

                compras_processadas += 1

            if not page.has_more:
                break
            pagina += 1
