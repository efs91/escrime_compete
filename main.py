import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import mysql.connector

class DatabaseManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Gestion de la base de données d'escrime")
        self.set_default_size(800, 600)

        self.connection = mysql.connector.connect(
            host="efs91.fr",
            user="escrime_compete",
            password="password",
            database="escrime_compete"
        )

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.create_joueurs_page()
        self.create_competitions_page()
        self.create_arbitres_page()

    def create_joueurs_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label("Joueurs"))

        self.joueurs_liststore = Gtk.ListStore(int, str, str, str, str, str, int)
        self.joueurs_treeview = Gtk.TreeView(model=self.joueurs_liststore)
        
        for i, column_title in enumerate(["ID", "Nom", "Prénom", "Club", "Sexe", "Nation", "Classement"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.joueurs_treeview.append_column(column)

        vbox.pack_start(self.joueurs_treeview, True, True, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(button_box, False, False, 0)

        add_button = Gtk.Button(label="Ajouter")
        add_button.connect("clicked", self.on_add_joueur)
        button_box.pack_start(add_button, True, True, 0)

        edit_button = Gtk.Button(label="Modifier")
        edit_button.connect("clicked", self.on_edit_joueur)
        button_box.pack_start(edit_button, True, True, 0)

        delete_button = Gtk.Button(label="Supprimer")
        delete_button.connect("clicked", self.on_delete_joueur)
        button_box.pack_start(delete_button, True, True, 0)

        self.load_joueurs_data()

    def load_joueurs_data(self):
        self.joueurs_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom, prenom, club, sexe, nation, classement FROM joueurs")
        for row in cursor:
            self.joueurs_liststore.append(list(row))
        cursor.close()

    def on_add_joueur(self, widget):
        dialog = JoueurDialog(self, "Ajouter un joueur", self.connection)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO joueurs (nom, prenom, club, sexe, nation, classement) VALUES (%s, %s, %s, %s, %s, %s)",
                (data['nom'], data['prenom'], data['club'], data['sexe'], data['nation'], data['classement'])
            )
            self.connection.commit()
            cursor.close()
            self.load_joueurs_data()

        dialog.destroy()


    def on_edit_joueur(self, widget):
        selection = self.joueurs_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            joueur_id = model[treeiter][0]
            dialog = JoueurDialog(self, "Modifier un joueur", self.connection, model[treeiter])
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE joueurs SET nom=%s, prenom=%s, club=%s, sexe=%s, nation=%s, classement=%s WHERE id=%s",
                    (data['nom'], data['prenom'], data['club'], data['sexe'], data['nation'], data['classement'], joueur_id)
                )
                self.connection.commit()
                cursor.close()
                self.load_joueurs_data()

            dialog.destroy()

    def on_delete_joueur(self, widget):
        selection = self.joueurs_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            joueur_id = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Êtes-vous sûr de vouloir supprimer ce joueur ?",
            )
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM joueurs WHERE id=%s", (joueur_id,))
                self.connection.commit()
                cursor.close()
                self.load_joueurs_data()
            dialog.destroy()

    def create_competitions_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label("Compétitions"))

        self.competitions_liststore = Gtk.ListStore(int, str, str, str, str)
        self.competitions_treeview = Gtk.TreeView(model=self.competitions_liststore)
        
        for i, column_title in enumerate(["ID", "Type de Compétition", "Formule", "Date Inscription", "Date Compétition"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.competitions_treeview.append_column(column)

        vbox.pack_start(self.competitions_treeview, True, True, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(button_box, False, False, 0)

        add_button = Gtk.Button(label="Ajouter")
        add_button.connect("clicked", self.on_add_competition)
        button_box.pack_start(add_button, True, True, 0)

        edit_button = Gtk.Button(label="Modifier")
        edit_button.connect("clicked", self.on_edit_competition)
        button_box.pack_start(edit_button, True, True, 0)

        delete_button = Gtk.Button(label="Supprimer")
        delete_button.connect("clicked", self.on_delete_competition)
        button_box.pack_start(delete_button, True, True, 0)

        self.load_competitions_data()

    def load_competitions_data(self):
        self.competitions_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, type_de_competition, formule, date_inscription, date_competition FROM competition")
        for row in cursor:
            self.competitions_liststore.append(list(row))
        cursor.close()

    def on_add_competition(self, widget):
        dialog = CompetitionDialog(self, "Ajouter une compétition")
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO competition (type_de_competition, formule, date_inscription, date_competition) VALUES (%s, %s, %s, %s)",
                (data['type_de_competition'], data['formule'], data['date_inscription'], data['date_competition'])
            )
            self.connection.commit()
            cursor.close()
            self.load_competitions_data()

        dialog.destroy()

    def on_edit_competition(self, widget):
        selection = self.competitions_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            competition_id = model[treeiter][0]
            dialog = CompetitionDialog(self, "Modifier une compétition", model[treeiter])
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE competition SET type_de_competition=%s, formule=%s, date_inscription=%s, date_competition=%s WHERE id=%s",
                    (data['type_de_competition'], data['formule'], data['date_inscription'], data['date_competition'], competition_id)
                )
                self.connection.commit()
                cursor.close()
                self.load_competitions_data()

            dialog.destroy()

    def on_delete_competition(self, widget):
        selection = self.competitions_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            competition_id = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Êtes-vous sûr de vouloir supprimer cette compétition ?",
            )
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM competition WHERE id=%s", (competition_id,))
                self.connection.commit()
                cursor.close()
                self.load_competitions_data()
            dialog.destroy()

    def create_arbitres_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label("Arbitres"))

        self.arbitres_liststore = Gtk.ListStore(int, str, str, str, str)
        self.arbitres_treeview = Gtk.TreeView(model=self.arbitres_liststore)
        
        for i, column_title in enumerate(["ID", "Nom", "Prénom", "Club", "Nation"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.arbitres_treeview.append_column(column)

        vbox.pack_start(self.arbitres_treeview, True, True, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(button_box, False, False, 0)

        add_button = Gtk.Button(label="Ajouter")
        add_button.connect("clicked", self.on_add_arbitre)
        button_box.pack_start(add_button, True, True, 0)

        edit_button = Gtk.Button(label="Modifier")
        edit_button.connect("clicked", self.on_edit_arbitre)
        button_box.pack_start(edit_button, True, True, 0)

        delete_button = Gtk.Button(label="Supprimer")
        delete_button.connect("clicked", self.on_delete_arbitre)
        button_box.pack_start(delete_button, True, True, 0)

        self.load_arbitres_data()

    def load_arbitres_data(self):
        self.arbitres_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom, prenom, club, nation FROM arbitres")
        for row in cursor:
            self.arbitres_liststore.append(list(row))
        cursor.close()

    def on_add_arbitre(self, widget):
        dialog = ArbitreDialog(self, "Ajouter un arbitre")
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO arbitres (nom, prenom, club, nation) VALUES (%s, %s, %s, %s)",
                (data['nom'], data['prenom'], data['club'], data['nation'])
            )
            self.connection.commit()
            cursor.close()
            self.load_arbitres_data()

        dialog.destroy()

    def on_edit_arbitre(self, widget):
        selection = self.arbitres_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            arbitre_id = model[treeiter][0]
            dialog = ArbitreDialog(self, "Modifier un arbitre", model[treeiter])
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE arbitres SET nom=%s, prenom=%s, club=%s, nation=%s WHERE id=%s",
                    (data['nom'], data['prenom'], data['club'], data['nation'], arbitre_id)
                )
                self.connection.commit()
                cursor.close()
                self.load_arbitres_data()

            dialog.destroy()

    def on_delete_arbitre(self, widget):
        selection = self.arbitres_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            arbitre_id = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Êtes-vous sûr de vouloir supprimer cet arbitre ?",
            )
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM arbitres WHERE id=%s", (arbitre_id,))
                self.connection.commit()
                cursor.close()
                self.load_arbitres_data()
            dialog.destroy()

class JoueurDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, joueur=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.connection = connection
        self.set_default_size(200, 200)

        box = self.get_content_area()

        self.nom_entry = Gtk.Entry()
        self.nom_entry.set_placeholder_text("Nom")
        box.add(self.nom_entry)

        self.prenom_entry = Gtk.Entry()
        self.prenom_entry.set_placeholder_text("Prénom")
        box.add(self.prenom_entry)

        self.club_entry = Gtk.Entry()
        self.club_entry.set_placeholder_text("Club")
        box.add(self.club_entry)

        self.sexe_combo = Gtk.ComboBoxText()
        self.sexe_combo.append_text("F")
        self.sexe_combo.append_text("M")
        self.sexe_combo.set_active(0)
        box.add(self.sexe_combo)

        self.nation_combo = Gtk.ComboBoxText()
        self.load_countries()
        box.add(self.nation_combo)

        self.classement_entry = Gtk.Entry()
        self.classement_entry.set_placeholder_text("Classement")
        box.add(self.classement_entry)

        if joueur:
            self.nom_entry.set_text(joueur[1])
            self.prenom_entry.set_text(joueur[2])
            self.club_entry.set_text(joueur[3])
            self.sexe_combo.set_active_id(joueur[4])
            self.nation_combo.set_active_id(joueur[5])
            self.classement_entry.set_text(str(joueur[6]))

        self.show_all()

    def load_countries(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM countries ORDER BY name")
        for row in cursor:
            self.nation_combo.append_text(row[0])
        cursor.close()
        # Set "France" as the active country if it exists in the list
        self.nation_combo.set_active(0)  # Set to the first item by default
        for i, country in enumerate(self.nation_combo.get_model()):
            if country[0] == "France":
                self.nation_combo.set_active(i)
                break

    def get_data(self):
        return {
            'nom': self.nom_entry.get_text(),
            'prenom': self.prenom_entry.get_text(),
            'club': self.club_entry.get_text(),
            'sexe': self.sexe_combo.get_active_text(),
            'nation': self.nation_combo.get_active_text(),
            'classement': int(self.classement_entry.get_text())
        }
class CompetitionDialog(Gtk.Dialog):
    def __init__(self, parent, title, competition=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(200, 200)

        box = self.get_content_area()

        self.type_entry = Gtk.Entry()
        self.type_entry.set_placeholder_text("Type de Compétition (classique ou division)")
        box.add(self.type_entry)

        self.formule_entry = Gtk.Entry()
        self.formule_entry.set_placeholder_text("Formule")
        box.add(self.formule_entry)

        self.date_inscription_entry = Gtk.Entry()
        self.date_inscription_entry.set_placeholder_text("Date d'Inscription (YYYY-MM-DD)")
        box.add(self.date_inscription_entry)

        self.date_competition_entry = Gtk.Entry()
        self.date_competition_entry.set_placeholder_text("Date de Compétition (YYYY-MM-DD)")
        box.add(self.date_competition_entry)

        if competition:
            self.type_entry.set_text(competition[1])
            self.formule_entry.set_text(competition[2])
            self.date_inscription_entry.set_text(competition[3])
            self.date_competition_entry.set_text(competition[4])

        self.show_all()

    def get_data(self):
        return {
            'type_de_competition': self.type_entry.get_text(),
            'formule': self.formule_entry.get_text(),
            'date_inscription': self.date_inscription_entry.get_text(),
            'date_competition': self.date_competition_entry.get_text()
        }

class ArbitreDialog(Gtk.Dialog):
    def __init__(self, parent, title, arbitre=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(200, 200)

        box = self.get_content_area()

        self.nom_entry = Gtk.Entry()
        self.nom_entry.set_placeholder_text("Nom")
        box.add(self.nom_entry)

        self.prenom_entry = Gtk.Entry()
        self.prenom_entry.set_placeholder_text("Prénom")
        box.add(self.prenom_entry)

        self.club_entry = Gtk.Entry()
        self.club_entry.set_placeholder_text("Club")
        box.add(self.club_entry)

        self.nation_entry = Gtk.Entry()
        self.nation_entry.set_placeholder_text("Nation")
        box.add(self.nation_entry)

        if arbitre:
            self.nom_entry.set_text(arbitre[1])
            self.prenom_entry.set_text(arbitre[2])
            self.club_entry.set_text(arbitre[3])
            self.nation_entry.set_text(arbitre[4])

        self.show_all()

    def get_data(self):
        return {
            'nom': self.nom_entry.get_text(),
            'prenom': self.prenom_entry.get_text(),
            'club': self.club_entry.get_text(),
            'nation': self.nation_entry.get_text()
        }

win = DatabaseManager()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
