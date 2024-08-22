import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def select_multiple_options(prompt, options):
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


def select_file(prompt, initial_dir):
    # Código para seleccionar un archivo
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=prompt, initialdir=initial_dir, filetypes=[("Text files", "*.txt")])
    root.destroy()
    return file_path

def main():
    # Opciones de equipos y archivos
    machine_options = ['Equipo 1', 'Equipo 2']
    eq1_options = ['PyS X06', 'EDW X06']
    eq2_options = ['PyS X06', 'EDW X06', 'PyS X15', 'EDW X15', 'PyS E06', 'PyS E09', 'PyS E12']

    # Pregunta al usuario qué equipos están seleccionados
    selected_machines = select_multiple_options('Seleccione el equipo:', machine_options)

    # Inicializa la lista para almacenar las rutas de los archivos seleccionados
    selected_files = []
    last_selected_path = '\\\\10.130.1.253\\FisicaQuilmes\\_Datos\\0_ QA Equipos\\0_ Files PROFILER'

    # Itera sobre los equipos seleccionados
    if selected_machines:
        for selected_machine in selected_machines:
            # Pide al usuario que seleccione las opciones de archivos para el equipo actual
            if selected_machine == 'Equipo 1':
                selected_options = select_multiple_options('Opciones para Equipo 1:', eq1_options)
            elif selected_machine == 'Equipo 2':
                selected_options = select_multiple_options('Opciones para Equipo 2:', eq2_options)
            
            # Itera sobre las opciones seleccionadas y pide al usuario que seleccione un solo archivo para cada opción
            if selected_options:
                for current_option in selected_options:
                    file_path = select_file(f'Seleccione un archivo para {current_option}', last_selected_path)
                    
                    if file_path:
                        # Agrega la ruta del archivo seleccionado
                        selected_files.append((file_path, current_option, selected_machine))
                        # Actualiza la carpeta del último archivo seleccionado
                        last_selected_path = os.path.dirname(file_path)

    # Fecha actual en formato DD/MM/AAAA
    current_date = datetime.now().strftime('%d_%m_%Y')

    # Itera sobre cada archivo seleccionado
    for file_path, option, machine in selected_files:
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        modified_content = file_content.replace(',', '.')
        name, ext = os.path.splitext(os.path.basename(file_path))
        modified_file_name = f'{option}_{machine}_modificado_{current_date}{ext}'
        
        # Guarda los archivos en el directorio especificado
        save_path = '\\\\10.130.1.253\\FisicaQuilmes\\_Datos\\0_ QA Equipos\\0_ Files PROFILER'
        modified_file_path = os.path.join(save_path, modified_file_name)
        
        with open(modified_file_path, 'w') as file:
            file.write(modified_content)
        
        messagebox.showinfo('Archivo modificado', f'Archivo modificado guardado como: {modified_file_name} en {save_path}')
        
        # Mueve los archivos originales a las carpetas correspondientes
        if 'Equipo 1' in machine:
            original_folder = '\\\\10.130.1.253\\FisicaQuilmes\\_Datos\\0_ QA Equipos\\0_ Files PROFILER\\Equipo 1 Subidos a QAT\\Originales'
        elif 'Equipo 2' in machine:
            original_folder = '\\\\10.130.1.253\\FisicaQuilmes\\_Datos\\0_ QA Equipos\\_ Files PROFILER\\Equipo 2 Subidos a QAT\\Originales'
        
        # Crea la carpeta de Originales si no existe
        os.makedirs(original_folder, exist_ok=True)
        
        # Mueve el archivo original
        shutil.move(file_path, os.path.join(original_folder, os.path.basename(file_path)))
        
        messagebox.showinfo('Archivo original movido', f'Archivo original movido a: {original_folder}')

if __name__ == '__main__':
    main()
