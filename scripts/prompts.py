{"EVAL_PROMPTS": {

    "0_shot" : """###ISTRUZIONI###
                    Sei un esperto in giurisprudenza. Di seguito ti verranno mostrati un testoe una domanda.
                    Il tuo compito è stabilire se la risposta alla domanda è contenuta nel testo.
                    Puoi utilizzare solo i seguenti due OUTPUT validi: ["SI", "NO"].
                    L'OUTPUT è "SI" se la la risposta alla domanda è contenuta nel testo.
                    L'OUTPUT è "NO" se la risposta alla domanda non è contenuta nel testo.
                    Per poter dire "SI" la risposta alla domanda deve essere strettamente e chiaramente nel testo.
                    Restituisci solamente "SI" o "NO" e null'altro.


                    ###TESTO###
                    {text}

                    ###DOMANDA###
                    {query}

                    OUTPUT: """,
    
    "2_shot": """###ISTRUZIONI###
    Sei un esperto in giurisprudenza. Di seguito ti verranno mostrati un testo e una domanda.
    Il tuo compito è stabilire se la risposta alla domanda è contenuta nel testo.
    Ti verranno mostrati due esempi.
    Il primo esempio indicato come ###ESEMPIO 1### mostra una risposta positiva.
    Il secondo esempio, idicato come ###ESEMPIO 2### mostra una risposta negativa.
    Puoi utilizzare solo i seguenti due OUTPUT validi: ["SI", "NO"].
    L'OUTPUT è "SI" se la la risposta alla domanda è contenuta nel testo.
    L'OUTPUT è "NO" se la risposta alla domanda non è contenuta nel testo.
    Per poter dire "SI" la risposta alla domanda deve essere strettamente e chiaramente nel testo come mostrato dall' ESEMPIO 1.
    Restituisci solamente "SI" o "NO" e null'altro.

    ###ESEMPIO 1###
    Testo:
    La capacità giuridica si acquista dal momento della nascita. I diritti che la legge riconosce a favore del concepito sono subordinati all'evento della nascita.

    DOMANDA:
    Quando si acquisice la capacità giuridica?

    OUTPUT: SI

    ###ESEMPIO 2###
    Testo:
    La capacità giuridica si acquista dal momento della nascita. I diritti che la legge riconosce a favore del concepito sono subordinati all'evento della nascita.

    DOMANDA:
    Quali diritti sono riconsciuti per legge al concepito?

    OUTPUT: NO

    ###TESTO INPUT###
    {text}

    ###DOMANDA###
    {query}

    OUTPUT: """
}

}