import tkinter as tk
from tkinter import filedialog, messagebox
import os
import ftplib
import pydicom

def select_multiple_options(prompt: str, options: list):
    """
    Muestra una ventana emergente para que el usuario seleccione una o varias opciones.

    Parameters
    ----------
    prompt : str
        El texto a mostrar en la ventana emergente.
    options : list
        Las opciones a presentar al usuario.

    Returns
    -------
    list
        Las opciones seleccionadas por el usuario. Si no se selecciona nada, devuelve None.
    """
    selected_items = []
    
    def on_select():
        selected_indices = listbox.curselection()
        nonlocal selected_items  # Referencia la variable de la función externa
        selected_items = [options[i] for i in selected_indices]
        root.quit()  # Finaliza el bucle principal

    root = tk.Tk()
    root.title("Seleccionar opciones")  # Título de la ventana

    # Agrega una etiqueta para mostrar el prompt
    label = tk.Label(root, text=prompt)
    label.pack(pady=10)

    listbox = tk.Listbox(root, selectmode='multiple')
    for option in options:
        listbox.insert(tk.END, option)
    listbox.pack(padx=20, pady=20)
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    select_button = tk.Button(button_frame, text="OK", command=on_select)
    select_button.pack(side=tk.LEFT, padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=root.quit)
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
    root.destroy()  # Destruye la ventana después de cerrar el bucle principal

    return selected_items if selected_items else None

def read_dcm_tag(filepath: str, tag: str):
    """
    Lee un archivo DICOM en `filepath` y devuelve el valor de la etiqueta (`tag`) dada.

    Si la etiqueta no se encuentra en el archivo, devuelve una cadena vacía.

    Si se produce una excepción al leer el archivo, imprime el mensaje de la excepción y devuelve una cadena vacía.

    Parámetros
    ----------
    filepath : str
        ruta al archivo DICOM a leer
    tag : str
        Nombre de la etiqueta a leer del archivo
    
    Returns
    -------
    str
        el valor de la etiqueta dada, o una cadena vacía si no se encuentra
    """
    try:
        ds = pydicom.dcmread(filepath,force=True)
        return ds.data_element(tag).value if tag in ds else ''
    except Exception as e:
        print(f'Error reading DICOM file {filepath}: {e}')
        return ''


def add_private_fields(path_file_name: str):
    # Obtener el directorio y nombre del archivo DICOM
    """
    Agrega un anexo en formato XML a un archivo DICOM y lo guarda en un archivo nuevo
    con el sufijo '_private.dcm'.
    
    Parámetros
    ----------
    path_file_name : str
        ruta al archivo DICOM a leer
    
    Returns
    -------
    None
    """
    
    dir_path = os.path.dirname(path_file_name)
    file_name = os.path.basename(path_file_name)
    
    # Ruta al archivo XML en el mismo directorio que el script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    xml_path = os.path.join(script_dir, 'anexo_XML.txt')

    # Leer el archivo XML
    with open(xml_path, 'rb') as xml_file:
        data_xml = xml_file.read()

    # Leer el archivo DICOM
    with open(path_file_name, 'rb') as dicom_file:
        data_dcm = dicom_file.read()

    # Buscar la posición de 'APPROVED' al final del archivo DICOM
    APPROVED = b'APPROVED'
    aux = len(data_dcm)
    i = 0
    while data_dcm[aux-8-i:aux-i] != APPROVED:
        i += 1

    # Reescribir el archivo DICOM agregando el anexo en XML
    data_dcm_mod = data_dcm[:aux-i]  # data2 cortado al final de 'APPROVED'
    output_path = os.path.join(dir_path, file_name[:-4] + '_private.dcm')
    with open(output_path, 'wb') as fid3:
        fid3.write(data_dcm_mod + data_xml)

    # Imprimir la ruta al archivo modificado
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Listo!", f"Archivo modificado guardado en: {output_path}")

def set_tolerances_to_qa(dicom_info):
    """
    Modifica la tabla de tolerancia de un archivo DICOM a QA.

    Args:
        dicom_info (pydicom.dataset.FileDataset): Información del archivo DICOM.
    """
    if hasattr(dicom_info, 'ToleranceTableSequence'):        
        tolerance_table = dicom_info.ToleranceTableSequence[0]

        tolerance_table.ToleranceTableNumber = 3
        tolerance_table.ToleranceTableLabel = 'T_QA'
        tolerance_table.GantryAngleTolerance = 180
        tolerance_table.BeamLimitingDeviceAngleTolerance = 90
        tolerance_table.PatientSupportAngleTolerance = 90
        tolerance_table.TableTopVerticalPositionTolerance = 2000
        tolerance_table.TableTopLongitudinalPositionTolerance = 2000
        tolerance_table.TableTopLateralPositionTolerance = 200
    for beam in dicom_info.BeamSequence:
        beam.ReferencedToleranceTableNumber = 3

def ui_get_dicom_file():
    """
    Opens a file dialog to select a DICOM file and returns the DICOM information, pixel data, file path, file name, and full name.

    This function opens a file dialog. The file dialog filters the files to only show DICOM files with the extension `.dcm`. If a file is selected, the file path is split to extract the file name and directory. The DICOM file is then read using `pydicom` to obtain the DICOM information and pixel data.

    Returns:
        tuple: [Dataset, numpy.ndarray or None, str, str, str]: A tuple containing the DICOM information (Dataset), pixel data (numpy.ndarray or None), file path (str), file name (str), and full name (str).
    """
    root = tk.Tk()
    root.withdraw()
    full_name = filedialog.askopenfilename(filetypes=[('DICOM Files', '*.dcm;*.img')])
    if full_name:
        file_path, file_name = os.path.split(full_name)  # Extract the directory and filename from the full path
        dicom_info = pydicom.dcmread(full_name,force=True)
        pixel_data = dicom_info.pixel_array if hasattr(dicom_info, 'pixel_array') else None
        return dicom_info, pixel_data, file_path, file_name, full_name
    else:
        return None, None, None, None, None
    
def get_dicom_file(full_name: str):
    """
    Lee un archivo DICOM en `full_name` y devuelve la información del archivo DICOM, los datos de píxel, la ruta del archivo y el nombre del archivo.

    Parámetros
    ----------
    full_name : str
        ruta al archivo DICOM a leer

    Returns
    -------
    tuple: [Dataset, numpy.ndarray or None, str, str]: Un tuple que contiene la información del archivo DICOM (Dataset), los datos de píxel (numpy.ndarray o None), la ruta del archivo (str) y el nombre del archivo (str).
    """
    file_path, file_name = os.path.split(full_name)  # Extract the directory and filename from the full path
    dicom_info = pydicom.dcmread(full_name,force=True)
    pixel_data = dicom_info.pixel_array if hasattr(dicom_info, 'pixel_array') else None
    return dicom_info, pixel_data, file_path, file_name

def get_dose_reference_sequence(dicom_info):
    """
    Devuelve la secuencia DoseReferenceSequence del archivo DICOM dado.

    Parámetros
    ----------
    dicom_info (pydicom.dataset.Dataset): La información del archivo DICOM que contiene la secuencia DoseReferenceSequence.

    Returns
    -------
    pydicom.sequence.Sequence: La secuencia DoseReferenceSequence del archivo DICOM.
    """ 
    return dicom_info.DoseReferenceSequence

def get_tolerace_table_sequence(dicom_info):   
    """
    Get the ToleranceTableSequence from the given DICOM info.

    Args:
        dicom_info (pydicom.dataset.Dataset): The DICOM info containing the ToleranceTableSequence.

    Returns:
        pydicom.sequence.Sequence: The ToleranceTableSequence from the DICOM info.
    """ 
    return dicom_info.ToleranceTableSequence

def get_fraction_group_sequence(dicom_info):
    """
    Returns the FractionGroupSequence from the given DICOM info.

    Args:
        dicom_info (pydicom.dataset.Dataset): The DICOM info containing the FractionGroupSequence.

    Returns:
        pydicom.sequence.Sequence: The FractionGroupSequence from the DICOM info.
    """
    return dicom_info.FractionGroupSequence

def get_beam_sequence(dicom_info):
    """
    Returns the BeamSequence from the given DICOM info.

    Args:
        dicom_info (pydicom.dataset.Dataset): The DICOM info containing the BeamSequence.

    Returns:
        pydicom.sequence.Sequence: The BeamSequence from the DICOM info.
    """
    return dicom_info.BeamSequence

def get_patient_setup_sequence(dicom_info):
    """
    Returns the PatientSetupSequence from the given DICOM info.

    Args:
        dicom_info (pydicom.dataset.Dataset): The DICOM info containing the PatientSetupSequence.

    Returns:
        pydicom.sequence.Sequence: The PatientSetupSequence from the DICOM info.
    """
    return dicom_info.PatientSetupSequence

def get_referenced_structure_set_sequence(dicom_info):
    """
    Returns the ReferencedStructureSetSequence from the given DICOM info.

    Args:
        dicom_info (pydicom.dataset.Dataset): The DICOM info containing the ReferencedStructureSetSequence.

    Returns:
        pydicom.sequence.Sequence: The ReferencedStructureSetSequence from the DICOM info.
    """
    return dicom_info.ReferencedStructureSetSequence

def get_number_of_beams(dicom_info):
    """
    Devuelve el numero de campos en el archivo DICOM dado, excluyendo los de SETUP.

    Parametros:
        dicom_info (pydicom.dataset.Dataset): La informacion del archivo DICOM

    Returns:
        int: El numero de campos en el archivo DICOM, excluyendo SETUP.
    """
    return len([beam for beam in dicom_info.BeamSequence if beam.TreatmentDeliveryType != "SETUP"])
