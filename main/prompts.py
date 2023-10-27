import platform
import stepping
import io
import commands

def code(debugger):
    target = debugger.GetSelectedTarget()
    code = stepping.get_source_code(target)
    
    return code

def codeInfo(debugger):
    target = debugger.GetSelectedTarget()
    code = stepping.get_source_code(target)
    
    if code is not None:
        if commands.modality == "api_key_mode":
            intro = f"Utilizzo il sistema {platform.platform()} su cui ho installato {stepping.get_lldb_version()} . Con LLDB sto facendo il debugging dell'eseguibile di '{stepping.get_sourceFile_path(target)}'. "
            code = f"Il codice sorgente è: \n{code}\n"
            conclusion = "Non devi rispondermi. Riceverari ulteriori info nel prossimo messaggio.\n"
        elif commands.modality == "browser_mode":
            intro = f"Utilizzo il sistema {platform.platform()} su cui ho installato {stepping.get_lldb_version()} . Con LLDB sto facendo il debugging dell'eseguibile di '{stepping.get_sourceFile_path(target)}'. "
            code = code.replace('\n','')
            code = f"Il codice sorgente è: {code} "
            conclusion = "Non devi rispondermi. Riceverari ulteriori info nel prossimo messaggio. "
        prompt = intro + code + conclusion

        return prompt
    else:
        return None

def stepInfo(debugger):
    if stepping.variables_to_be_sent is True:
        target = debugger.GetSelectedTarget()
        cline = stepping.get_current_line(target)
        vars = stepping.get_local_variables(target)

        if cline and vars is not None:
            if commands.modality == "api_key_mode":
                intro = f"In questo momento: \n"
                current_line = f"   1. La linea corrente è la numero: {cline} .\n"
                output_string = io.StringIO()
                output_string.write("   2. Le variabili nel blocco sono: \n")
                for i, var in enumerate(vars):
                    output_string.write(f"        - La variabile {i+1} ha nome '{var[0]}', valore '{var[1]}', tipo '{var[2]}' e indirizzo '{var[3]}' .\n")
                variables = output_string.getvalue()
                output_string.close()
                conclusion = "Non devi rispondermi. Ti fornirò le mie richieste al prossimo messaggio.\n"
            elif commands.modality == "browser_mode":
                intro = f"In questo momento: "
                current_line = f"   1. La linea corrente è la numero: {cline} . "
                output_string = io.StringIO()
                output_string.write("   2. Le variabili nel blocco sono: ")
                for i, var in enumerate(vars):
                    output_string.write(f"        - La variabile {i+1} ha nome '{var[0]}', valore '{var[1]}', tipo '{var[2]}' e indirizzo '{var[3]}' . ")
                variables = output_string.getvalue()
                output_string.close()
                conclusion = "Non devi rispondermi. Ti fornirò le mie richieste al prossimo messaggio. "
            prompt = intro + current_line + variables + conclusion

            return prompt
        else:
            return None

    else:
        prompt = ""
        return prompt

def automatedDebuggingInfo(debugger):
    program_output = stepping.automated_debugging(debugger)
    program_output = f"L'output del programma è il seguente: '{program_output}'. "

    if stepping.blocking_errors is True:
        if stepping.memory_read_failed is False:
            debugging_result = f"Il programma durante il debugging si è interrotto alla linea {stepping.line_of_crash}. La ragione dello stop è: {stepping.sig_detected}. "
        elif stepping.memory_read_failed is True:
            debugging_result = f"Il programma durante il debugging si è interrotto. La ragione dello stop è: {stepping.sig_detected}. "
    elif stepping.blocking_errors is False:
        debugging_result = "Il programma durante il debugging ha concluso la sua esecuzione senza interruzioni. "
    
    if commands.modality == "api_key_mode":
        ask_for_errors = "Quanti e quali sono gli errori del codice? Differenziali per tipologia.\n"
    elif commands.modality == "browser_mode":
        ask_for_errors = "Quanti e quali sono gli errori del codice? Differenziali per tipologia. "   
    prompt = program_output + debugging_result + ask_for_errors

    return prompt

def sourceFile_name(debugger):
    target = debugger.GetSelectedTarget()
    name = stepping.get_sourceFile_name(target)
    
    if name is not None:
        return name
    else:
        return None
