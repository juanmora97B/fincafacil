import customtkinter as ctk
from tkinter import ttk


def get_theme_colors():
    """Devuelve colores adaptativos según el modo de apariencia actual."""
    modo = ctk.get_appearance_mode()
    fg_card = "#2B2B2B" if modo == "Dark" else "#F5F5F5"
    sel = "#1976D2" if modo == "Light" else "#1F538D"
    hover = "#90caf9" if modo == "Light" else "#14375E"
    text_on_bg = "white" if modo == "Dark" else "black"
    return {
        "mode": modo,
        "fg": fg_card,
        "sel": sel,
        "hover": hover,
        "text": text_on_bg,
    }


def style_treeview():
    """Aplica un estilo base a ttk.Treeview acorde al tema actual."""
    colors = get_theme_colors()
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        "Treeview",
        background=colors["fg"],
        fieldbackground=colors["fg"],
        foreground=colors["text"],
        rowheight=28
    )
    style.map("Treeview", background=[('selected', colors["sel"])])


def add_tooltip(widget, text):
    """Agrega un tooltip mejorado con manejo robusto de destrucción."""
    try:
        tooltip_window = [None]
        schedule_id = [None]
        
        def destruir_tooltip():
            """Destruye el tooltip de forma segura"""
            if schedule_id[0] is not None:
                try:
                    widget.after_cancel(schedule_id[0])
                    schedule_id[0] = None
                except:
                    pass
            
            if tooltip_window[0] is not None:
                try:
                    tooltip_window[0].destroy()
                except:
                    pass
                finally:
                    tooltip_window[0] = None
        
        def crear_tooltip():
            """Crea el tooltip después del delay"""
            try:
                if not widget.winfo_exists():
                    return
                
                tooltip_window[0] = ctk.CTkToplevel(widget)
                tooltip_window[0].wm_overrideredirect(True)
                tooltip_window[0].wm_attributes("-topmost", True)
                
                try:
                    x = widget.winfo_rootx() + 40
                    y = widget.winfo_rooty() + 20
                    tooltip_window[0].geometry(f"+{x}+{y}")
                except:
                    destruir_tooltip()
                    return
                
                label = ctk.CTkLabel(
                    tooltip_window[0], 
                    text=text, 
                    font=("Segoe UI", 10), 
                    fg_color="#333", 
                    text_color="#fff", 
                    corner_radius=6
                )
                label.pack(ipadx=8, ipady=4)
                
            except:
                destruir_tooltip()
        
        def on_enter(event):
            destruir_tooltip()
            schedule_id[0] = widget.after(500, crear_tooltip)
        
        def on_leave(event):
            destruir_tooltip()
        
        def on_destroy(event):
            destruir_tooltip()
        
        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")
        widget.bind("<Destroy>", on_destroy, add="+")
        
    except:
        pass


# Funciones de diálogo UI
def mostrar_error(titulo, mensaje):
    """Muestra un diálogo de error."""
    from tkinter import messagebox
    messagebox.showerror(titulo, mensaje)


def mostrar_exito(titulo, mensaje):
    """Muestra un diálogo de éxito."""
    from tkinter import messagebox
    messagebox.showinfo(titulo, mensaje)


def mostrar_advertencia(titulo, mensaje):
    """Muestra un diálogo de advertencia."""
    from tkinter import messagebox
    messagebox.showwarning(titulo, mensaje)


def mostrar_info(titulo, mensaje):
    """Muestra un diálogo de información."""
    from tkinter import messagebox
    messagebox.showinfo(titulo, mensaje)
