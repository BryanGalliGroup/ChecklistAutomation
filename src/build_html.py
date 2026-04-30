from html import escape

def build_email_html(body: str, signature: str, image_url: str | None) -> str:
    image_html = ""

    if image_url:
        image_html = f"""
        <div style="text-align: flex-start; margin: 24px 0;">
            <img 
                src="{escape(image_url)}" 
                alt="Imagem do checklist" 
                style="max-width: 600px; width: 45%; height: auto;"
            />
        </div>
        """

    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6;">
            <div style="white-space: pre-line;">
                {escape(body)}
            </div>

            <hr style="margin: 32px 0;" />

            <h3 style="text-align: center;">
                Automação de Checklist
            </h3>

            <p>
                Este é o resumo das atividades realizadas hoje, gerado automaticamente a partir das alterações realizadas no projeto.
            </p>

            <p>
                O objetivo é fornecer uma visão clara e concisa das mudanças, melhorias e correções implementadas,
                facilitando o acompanhamento do progresso e o entendimento dos impactos positivos das alterações realizadas.
            </p>

            <p>
                O resumo é gerado a partir dos commits(alterações no código) realizados no dia, utilizando inteligência artificial para sintetizar as informações de forma clara e objetiva.
                A inteligência artificial pode cometer erros ou interpretar de forma incorreta as informações, portanto, caso tenha dúvidas ou queira mais detalhes sobre alguma atividade, sinta-se à vontade para entrar em contato.
            </p>

            <hr style="margin: 32px 0;" />

            {image_html}

            <div style="white-space: pre-line; color: #8c8c8c; font-size: 0.9em;">
                {escape(signature)}
            </div>
        </body>
    </html>
    """.strip()