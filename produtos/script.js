const input = document.getElementById("input");
const respostaEl = document.getElementById("resposta");
const produtosDiv = document.getElementById("produtos");
const btnEnviar = document.getElementById("btn-enviar");

const placeholderImage =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='800'%3E%3Crect width='100%25' height='100%25' fill='%23eaf0f9'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='28' fill='%2372869b'%3ESem imagem%3C/text%3E%3C/svg%3E";

function setLoading(isLoading) {
    if (!btnEnviar) {
        return;
    }

    btnEnviar.disabled = isLoading;
    btnEnviar.textContent = isLoading ? "A procurar..." : "Pesquisar";
}

function formatPrice(preco) {
    if (!preco) {
        return "Preco indisponivel";
    }
    return `${preco}EUR`;
}

function renderProdutos(produtos) {
    if (!Array.isArray(produtos) || produtos.length === 0) {
        produtosDiv.innerHTML = "";
        return;
    }

    produtosDiv.innerHTML = produtos
        .map((p, index) => {
            const nome = p.nome || "Sem nome";
            const preco = formatPrice(p.preco);
            const imagem = p.imagem || placeholderImage;
            const link = p.link || "#";
            const target = p.link ? "_blank" : "_self";

            return `
                <article class="produto" style="animation-delay:${index * 0.05}s">
                    <img src="${imagem}" alt="${nome}">
                    <h3>${nome}</h3>
                    <p>${preco}</p>
                    <a href="${link}" target="${target}" rel="noopener noreferrer">Ver produto</a>
                </article>
            `;
        })
        .join("");
}

async function enviar() {
    const mensagem = input.value.trim();

    if (!mensagem) {
        respostaEl.innerText = "Escreve uma pergunta.";
        produtosDiv.innerHTML = "";
        return;
    }

    setLoading(true);

    try {
        const res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: mensagem })
        });

        const data = await res.json();

        respostaEl.innerText = data.resposta || "Sem resposta.";
        renderProdutos(data.produtos);
    } catch (error) {
        respostaEl.innerText = "Erro ao ligar ao servidor.";
        produtosDiv.innerHTML = "";
        console.error(error);
    } finally {
        setLoading(false);
    }
}

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        enviar();
    }
});
