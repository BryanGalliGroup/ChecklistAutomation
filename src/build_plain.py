def build_plain_body(body: str, signature: str) -> str:
    return f"""
{body}

============================================================================================
                                                                    Automação de Checklist
============================================================================================

Este é o resumo das atividades realizadas hoje, gerado automaticamente a partir das alterações realizadas no projeto.

O objetivo é fornecer uma visão clara e concisa das mudanças, melhorias e correções implementadas, facilitando o 
acompanhamento do progresso e o entendimento dos impactos positivos das alterações realizadas.

============================================================================================

{signature}
""".strip()