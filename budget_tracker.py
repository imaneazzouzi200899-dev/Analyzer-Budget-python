import sqlite3
import pyttsx3
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk,messagebox
from datetime import datetime
def load_data():
     try:
          conn = sqlite3.connect("budget_data.db")
          c = conn.cursor()
          c.execute("SELECT * FROM expenses")
          rows = c.fetchall()
          for row in rows:
               tableau.insert("","end", values=row)
          conn.close()
          calculer_total()
     except:
          pass
app = tk.Tk()
app.title("Budget Tracker pro Edition France")
app.geometry("400x500")
def task_audio(montant, categorie,total):
    try:
        engine=pyttsx3.init()
        engine.say(f"{montant} euros pour {categorie}")
        engine.say(f"Le total est {total} euros")
        engine.runAndWait()
    except Exception as e:
         print(f"Error:{e}")
def calculer_total():
    total= 0.0
    for i in tableau.get_children():
            valeurs = tableau.item(i) ['values']
            if valeurs:
                 try:
                     total += float(valeurs[0])
                 except: 
                      continue
    label_total.config(text=f"Total:{total} €")
    if total>500:
     label_total.config(fg="red")
    else:
         label_total.config(fg="green")
    return total
def afficher_statistiques():
    try:
        conn = sqlite3.connect('budget_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT categorie, SUM(montant) FROM expenses GROUP BY categorie")
        data = cursor.fetchall()
        conn.close()
        if not data:
            messagebox.showinfo("Info","pas de données pour générer le graphique.")
            return
        categories = [row[0] for row in data]
        montants = [row[1] for row in data]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories,montants, color= ['#4CAF50','#2196F3','#FF9800','#F44336','#9C27B0'])
        plt.title('Analyse des Dépenses par catégorie', fontsize=14, fontweight='bold')
        plt.xlabel('catégories',fontsize=12)
        plt.ylabel('Montant (€)',fontsize=12)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x()+bar.get_width()/2,yval + 5, f'{yval}€', ha='center', va='bottom')
            plt.grid(axis='y',linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Erreur",f"Impossible de générer le graphique : {e}")
def ajouter_depense(): 
    print
    montant = entry_montant.get()
    categorie = combo_cat.get()
    if not montant or not categorie:
         messagebox.showwarning("Attention","Veullez remplir tout les champs")
         return 
    try:
         import datetime
         now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
         tableau.insert("","end",values=(montant,categorie,now)) 
         import sqlite3
         conn = sqlite3.connect("budget_data.db")
         c =conn.cursor()
         c.execute("CREATE TABLE IF NOT EXiSTS expenses (montant REAL, categorie Text, date TEXT)")
         c.execute("INSERT INTO expenses VALUES(?,?,?)", (montant, categorie, now))
         conn.commit()
         conn.close()
         entry_montant.delete(0,'end')
         combo_cat.set('')
         total_reel=calculer_total()
         import threading
         threading.Thread(target=speak_task, args=(montant,categorie,total_reel),daemon=True).start()
    except Exception as e:
         print(f"Erreur lors de l'ajout:{e}")
def speak_task(montant,categorie,total_reel):
       import pyttsx3
       engine = pyttsx3.init()
       print(f"DEBUG:Total recu est {total_reel}")
       text_to_say = f"Ajouté{montant} euros pour {categorie}"
       try:
         valeur =int(float(total_reel))
         if valeur >=500:
             text_to_say += "Attention! budget dépassé"
       except Exception as e:
           print(f"Erreur de conversion: {e}")
       engine.say(text_to_say)
       engine.runAndWait()
       engine.stop()
def supprimer():
    selected = tableau.selection()
    if selected:
        for item in selected:
            tableau.delete(item)
            calculer_total()
        else:
           messagebox.showwarning("Attention", "Veuillez sélectionner une ligne")  
def reset():
        if messagebox.askyesno("Reset","Voulez_vous tout effacer ?"):
           for i in tableau.get_children():
            tableau.delete(i)
            label_total.config(text="Total:0 €", fg="blue")
label_titre =tk.Label(app,text="Gestionnaire de Budget",font=("Arial",16,"bold"))
label_titre.pack(pady=15) 
tk.Label(app,text="Montant(€):").pack()
entry_montant = tk.Entry(app,font=("Arial", 12))
entry_montant.pack(pady=5) 
tk.Label(app,text="Catégorie:").pack()
categories = ["Nourriture","Loyer", "ETUDES","Loisirs","Transport"]
combo_cat = ttk.Combobox(app,values=categories,font=("Arial",10))
combo_cat.pack(pady=5)
btn_ajouter = tk.Button(app,text="Ajouter a la liste",command=ajouter_depense, bg="#4CAF50", fg="white",font=("Arial", 10, "bold"))
btn_ajouter.pack(pady=15)
btn_delete = tk.Button(app,text="Supprimer sélection", bg="orange", command=supprimer)
btn_delete.pack(pady=5)
btn_reset = tk.Button(app,text="Réinitialiser", bg="#f44336",fg="white",command=reset)
btn_reset.pack(pady=5)
columns = ("Montant","Catégorie","Date")
tableau = ttk.Treeview(app,columns=columns, show="headings",height=8)
tableau.heading("Montant",text="Montant(€)")
tableau.heading("Catégorie",text="Catégorie")
tableau.heading("Date",text="Date et Heure")
tableau.pack(pady=10, fill="x",padx=10)
label_total = tk.Label(app,text="Total: 0 €", font=("Arial",14,"bold"), fg="blue")
label_total.pack(pady=20)
load_data()
btn_stats = tk.Button(app,text="Analyse des dépenses",bg="#2196F3", fg="white",font=("Arial", 10, "bold"),command=afficher_statistiques)
btn_stats.pack(pady=10)
app.mainloop() 