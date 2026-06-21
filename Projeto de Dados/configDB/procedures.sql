USE SALES;
GO

-- Criação de Procedimentos Armazenados

CREATE PROCEDURE filtroEstado
    @loja VARCHAR(50)
AS
BEGIN
    SELECT  id_compra as [ID da Compra],
			CONVERT(DATE, data) as [Data da Compra],
			loja as [Loja],
			vendedor as Vendedor,
			produto as Produto,
			nome_cliente as [Nome do Cliente],
				CASE genero_cliente
					WHEN 'M' THEN 'Masculino'
					WHEN 'F' THEN 'Feminino'
					WHEN 'Outro' THEN 'Outro'
					ELSE 'Não informado'
				END AS [Gênero]
    FROM Compras

	WHERE Loja = @loja
END;
GO

---------------------------------------

CREATE PROCEDURE comprasPorVendedor
	@vendedor VARCHAR(255)
AS
BEGIN
	SELECT  Vendedor, 
			CONVERT(DATE, data) as [Data da compra],
			loja as Loja,
			Produto,
			Nome_cliente as Cliente,
			forma_pagamento as [Forma de Pagamento]


	FROM COMPRAS
	WHERE Vendedor = @vendedor
	ORDER BY data DESC
END

---------------------------------------
CREATE PROCEDURE rankingVendedores
AS
BEGIN
	SELECT COUNT(id_compra) AS [Quantidade de Vendas], 
	VENDEDOR as Vendedor

	FROM COMPRAS
	GROUP BY VENDEDOR
END;

---------------------------------------

CREATE PROCEDURE rankingFormasPagamento 
AS
BEGIN
	SELECT COUNT(id_compra) as [Quantidade de compras],
		   forma_pagamento as [Forma de Pagamento]
	FROM Compras
	GROUP BY forma_pagamento
END

----------------------------------------

CREATE PROCEDURE rankingProdutos
AS
BEGIN
	SELECT COUNT(a.id_compra) as [Quantidade de compras], a.produto as Produtos, SUM(b.preco) as [Total Adquirido em Reais]
	from Compras as A
	INNER JOIN Produtos as B
		ON A.id_produto = B.id_produto
	Group by a.produto, b.preco
END


-----------------------------------------


CREATE PROCEDURE rankingGenero
AS
BEGIN
	SELECT  COUNT(id_compra) as [Quantidade de Compras],
					CASE genero_cliente
						WHEN 'M' THEN 'Masculino'
						WHEN 'F' THEN 'Feminino'
						WHEN 'O' THEN 'Outros'
						ELSE 'Não informado'
					END AS [Gênero]
	FROM COMPRAS
	Group by genero_cliente
END

------------------------------------------
-- Execução dos Procedimentos Armazenados

--EXEC filtroEstado '';
--EXEC rankingVendedores;
--EXEC rankingFormasPagamento
--EXEC rankingProdutos;
--EXEC comprasPorVendedor '';
--EXEC rankingGenero;