'''
This is a Volatility plugin that checks a system memory dump for processes that are not protected by ASLR.
'''

from typing import Callable, List

from volatility3.framework import constants, exceptions, interfaces, renderers
from volatility3.framework.configuration import requirements
from volatility3.framework.renderers import format_hints
from volatility3.framework.symbols import intermed
from volatility3.framework.symbols.windows import extensions
from volatility3.plugins.windows import pslist

import io
import logging
import os
import pefile

vollog = logging.getLogger(__name__)

IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE = 0X0040
IMAGE_FILE_RELOCS_STRIPPED = 0X0001

def check_aslr(pe):                         # take a PE file object as lone parameter and return the status of ASLR
    pe.parse_data_directories([
        pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG']
    ])
    dynamic = False
    stripped = False

    if (pe.OPTIONAL_HEADER.DllCharacteristics & IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE):        # was the PE compiled with the DYNAMIC base setting?
        dynamic = True
    if pe.FILE_HEADER.Characteristics & IMAGE_FILE_RELOCS_STRIPPED:         # has the file relocation data been stripped out?
        stripped = True
    if not dynamic or (dynamic and stripped):
        aslr = False    # if it isn't dynamic, or has been stripped of it's relocation data since being compiled, there is no ASLR protection
    else:
        aslr = True
    return aslr

class AslrCheck(interfaces.plugins.PluginInterface):            # inherit from the PluginInterface object

    @classmethod
    def get_requirements(cls):      # we need the memory layer, symbols tables, and pslist plugin
        return [
            requirements.TranslationLayerRequirement(                       # memory layer is required
                name='primary', description='Memory layer for the kernel',
                architectures=["Intel32", "Intel64"]
            ),

            requirements.SymbolTableRequirement(                            # symbols tables are required
                name="nt_symbols", description="Windows kernel symbols"
            ),

            requirements.PluginRequirement(                                 # pslist plugin is required
                name='pslist', plugin=pslist.PsList, version=(1, 0, 0), optional = True
            ),

            requirements.ListRequirement(name = 'pid',              # this is an option to pass in a list of PIDs to check instead of checking all
                                         element_type = int,
                                         description = "Process ID to include (all others are excluded)",
                                         optional = True),
        ]
    
    @classmethod                        # this method filters PIDs; return True if the PID is not on the list, False if it is
    def create_pid_filter(cls, pid_list: List[int] = None) -> Callable[[interfaces.objects.ObjectInterface], bool]:
        filter_func = lambda _: False
        pid_list = pid_list or []
        filter_list = [x for x in pid_list if x is not None]
        if filter_list:
            filter_func = lambda x: x.UniqueProcessId not in filter_list
        return filter_func
    

    def _generator(self, procs):
        pe_table_name = intermed.IntermediateSymbolTable.create(        # data structure to use for each process in memory
            self.context,
            self.config_path,
            "windows",
            "pe",
            class_types=extensions.pe.class_types
        )

        procnames = list()
        for proc in procs:
            procname = proc.ImageFileName.cast("string", max_length=proc.ImageFileName.vol.count, errors='replace')
            if procname in procnames:
                continue
            procnames.append(procname)

            proc_id = "Unknown"
            try:
                proc_id = proc.UniqueProcessId
                proc_layer_name = proc.add_process_layer()
            except exceptions.InvalidAddressException as e:
                vollog.error(f"Process {proc_id}: Invalid address {e} in layer {e.layer_name}")
                continue

            peb = self.context.object(                              # variablize the PEB memory region contents
                self.config['nt_symbols'] + constants.BANG + "_PEB",
                layer_name = proc_layer_name,
                offset = proc.Peb
            )

            try:
                dos_header = self.context.object(
                    pe_table_name + constants.BANG + "_IMAGE_DOS_HEADER",
                    offset=peb.ImageBaseAddress,
                    layer_name=proc_layer_name
                )
            except Exception as e:
                continue

            pe_data = io.BytesIO()
            for offset, data in dos_header.reconstruct():
                pe_data.seek(offset)
                pe_data.write(data)
            pe_data_raw = pe_data.getvalue()            # writing the contents of PEB into a file-like object (pe_data)
            pe_data.close()

            try:
                pe = pefile.PE(data=pe_data_raw)        # create a PE file object based on the PEB of the process in question
            except Exception as e:
                continue

            aslr = check_aslr(pe)                       # now check the aslr status of the constructed PE file object

            yield (0, (proc_id,             # for each process, yield a tuple containing the PID, process name, base address, and ASLR status (boolean)
                       procname,
                       format_hints.Hex(pe.OPTIONAL_HEADER.ImageBase),
                       aslr,
                       ))
            
    def run(self):
        procs = pslist.PsList.list_processes(self.context,              # get the list of processes by calling the pslist plugin
                                             self.config["primary"],
                                             self.config["nt_symbols"],
                                             filter_func = self.create_pid_filter(self.config.get('pid', None)))
        return renderers.TreeGrid([             # return the data from the generator (using the TreeGrid renderer)
            ("PID", int),
            ("Filename", str),
            ("Base", format_hints.Hex),
            ("ASLR", bool)],
            self._generator(procs))
    