import subprocess
import lldb
import os

def get_lldb_version():
    lldb_version = subprocess.run("lldb -v", shell=True, capture_output=True, text=True, check=True)
    lldb_version = lldb_version.stdout.replace("\n", "")
    return lldb_version

def get_frame(target):
    process = target.GetProcess()
    if not process.IsValid():
        return 

    thread = process.GetThreadAtIndex(0)
    if not thread.IsValid():
        return 

    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        return 
    
    return frame

def get_current_line(target):
    try:
        line = get_frame(target).GetLineEntry().GetLine()
        return line
    except:
        return None

def get_sourceFile_name(target):
    try:
        frame = get_frame(target)
        file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
        return file_name
    except:
        print("You have to set a breakpoint and run the target first")

def get_sourceFile_path(target):
    try:
        frame = get_frame(target)
        dirName = frame.GetLineEntry().GetFileSpec().GetDirectory()
        fileName = get_sourceFile_name(target)
        sourceFilePath = dirName+"/"+fileName
        return sourceFilePath
    except:
        sourceFilePath = None
        print("You have to set a breakpoint and run the target first")

def source_code_in_array(filePath):
    try:
        lines = []
        with open(filePath, "r") as file:
            for line in file:
                lines.append(line.rstrip('\n'))

        return lines

    except FileNotFoundError:
        print(f"Error: File '{filePath}' not found")
        return []
    
def add_numbers_to_lines(lines):
    for i, line in enumerate(lines):
        lines[i] = f"    {(i+1):>3}   {line}"
    return lines
    
def get_source_code(target):
    path=get_sourceFile_path(target)
    if path is not None:
        lines = source_code_in_array(path)
        lines = add_numbers_to_lines(lines)

        return '\n'.join(lines)
    else:
        return None

def get_local_variables(target):
    try:
        vars = []
        vars = get_frame(target).get_locals() #Alternatively, use: get_all_variables().

        variables = []
        for var in vars:
            variable = [var.GetName(), var.GetValue(), var.GetTypeName(), var.GetLoadAddress()]
            variables.append(variable)

        return variables
    except:
        return None

sig_detected = ""
variables_to_be_sent = True
blocking_errors = False
def automated_debugging(debugger):
    global line_of_crush, sig_detected, variables_to_be_sent, blocking_errors, memory_read_failed
    target = debugger.GetSelectedTarget()
    target.DeleteAllBreakpoints()
    target.BreakpointCreateByName("main")
    process = target.GetProcess()
    if process.IsValid():
        process.Kill()
    
    executable_dir = target.GetExecutable().GetDirectory()
    executable_filename = target.GetExecutable().GetFilename()
    executable_path = os.path.join(executable_dir, executable_filename)
    proc = subprocess.Popen(executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #In case of blocking error it is not guaranteed the full output.
    output, error = proc.communicate()
    output_string = output + error
    output_string = output_string.replace('\n',' ')

    process = target.LaunchSimple(None, None, None)
    print("----------------- Execution Started -------------------")
    
    while process.GetState() != lldb.eStateExited:
        debugging_file = get_sourceFile_path(target)
        line_of_crush = get_current_line(target)
        thread = process.GetThreadAtIndex(0)
        thread.StepOver()

        memory_read_failed = False
        stop_reason = thread.GetStopReason()
        if stop_reason == lldb.eStopReasonSignal:
            signal_info = thread.GetStopDescription(256)
            if "SIGABRT" in signal_info:
                sig_detected = "SIGABRT"
            elif "SIGSEGV" in signal_info:
                sig_detected = "SIGSEGV indirizzo non valido"

                frame = target.GetProcess().GetSelectedThread().GetSelectedFrame()
                address = frame.GetPCAddress()
                memory_data = target.ReadMemory(address, 4, lldb.SBError())
                if memory_data is None:
                    memory_read_failed = True
                    variables_to_be_sent = False
            elif "SIGFPE" in signal_info:
                sig_detected = "SIGFPE"
            else:
                sig_detected = signal_info
    
            if sig_detected != "":
                target.DeleteAllBreakpoints()
                if memory_read_failed is False:
                    target.BreakpointCreateByLocation(debugging_file, line_of_crush)
                else:
                    target.BreakpointCreateByName("main")
                if process.IsValid() and process.GetState() == lldb.eStateStopped:
                    process.Kill()
                    print("---------------- Execution Terminated -----------------")

                stdout_fd = os.dup(1)
                os.close(1)
                os.open(os.devnull, os.O_WRONLY)
                process = target.LaunchSimple(None, None, None)
                os.dup2(stdout_fd, 1)
                os.close(stdout_fd)

                blocking_errors = True
                break
    
    if process.GetState() == lldb.eStateExited and process.GetExitStatus() == 0:
        print("---------------- Execution Terminated -----------------")
        stdout_fd = os.dup(1)
        os.close(1)
        os.open(os.devnull, os.O_WRONLY)
        process = target.LaunchSimple(None, None, None)
        os.dup2(stdout_fd, 1)
        os.close(stdout_fd)

        variables_to_be_sent = False
        blocking_errors = False

    return output_string
