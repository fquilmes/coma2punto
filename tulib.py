import tkinter as tk
from tkinter import filedialog
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

    Devuelve
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