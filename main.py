import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import mysql.connector
import datetime

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

        self.create_competitions_page()

    def create_competitions_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Compétitions"))

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

        manage_button = Gtk.Button(label="Gérer la compétition")
        manage_button.connect("clicked", self.on_manage_competition)
        button_box.pack_start(manage_button, True, True, 0)

        self.load_competitions_data()

    def load_competitions_data(self):
        self.competitions_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, type_de_competition, formule, date_inscription, date_competition FROM competition")
        for row in cursor:
            row = list(row)
            for i, value in enumerate(row):
                if isinstance(value, datetime.date):
                    row[i] = value.strftime('%Y-%m-%d')  # Convertir en chaîne de caractères
            self.competitions_liststore.append(row)
        cursor.close()


    def on_add_competition(self, widget):
        dialog = CompetitionDialog(self, "Ajouter une compétition", self.connection)
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
            dialog = CompetitionDialog(self, "Modifier une compétition", self.connection, model[treeiter])
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

    def on_manage_competition(self, widget):
        selection = self.competitions_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            competition_id = model[treeiter][0]
            competition_type = model[treeiter][1]
            dialog = ManageCompetitionWindow(self, self.connection, competition_id, competition_type)
            dialog.show_all()

class ManageCompetitionWindow(Gtk.Window):
    def __init__(self, parent, connection, competition_id, competition_type):
        Gtk.Window.__init__(self, title="Gérer la compétition")
        self.set_default_size(800, 600)
        self.connection = connection
        self.competition_id = competition_id
        self.competition_type = competition_type

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.create_competition_page()
        self.create_joueurs_page()
        self.create_arbitres_page()

    def create_competition_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Compétition"))

        self.groups_liststore = Gtk.ListStore(int, str)
        self.groups_treeview = Gtk.TreeView(model=self.groups_liststore)
        
        for i, column_title in enumerate(["Groupe", "Joueurs"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.groups_treeview.append_column(column)

        vbox.pack_start(self.groups_treeview, True, True, 0)

        launch_button = Gtk.Button(label="Lancer la compétition")
        launch_button.connect("clicked", self.on_launch_competition)
        vbox.pack_start(launch_button, False, False, 0)

    def on_launch_competition(self, widget):
        if self.competition_type == "classique":
            self.launch_classique_competition()

    def launch_classique_competition(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom, prenom FROM joueurs")
        joueurs = cursor.fetchall()
        cursor.close()

        groupes = [joueurs[i:i + 5] for i in range(0, len(joueurs), 5)]

        self.groups_liststore.clear()
        for idx, groupe in enumerate(groupes, 1):
            joueurs_str = ", ".join([f"{joueur[1]} {joueur[2]}" for joueur in groupe])
            self.groups_liststore.append([idx, joueurs_str])

    def create_joueurs_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Joueurs"))

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
        cursor.execute("SELECT id, nom, prenom, club, sexe, nation, classement FROM joueurs WHERE id_compete = %s", (self.competition_id,))
        for row in cursor:
            self.joueurs_liststore.append(list(row))
        cursor.close()


    def on_add_joueur(self, widget):
        dialog = JoueurDialog(self, "Ajouter un joueur", self.connection, self.competition_id)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO joueurs (nom, prenom, club, sexe, nation, classement, id_compete) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (data['nom'], data['prenom'], data['club'], data['sexe'], data['nation'], data['classement'], self.competition_id)
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

    def create_arbitres_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Arbitres"))

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
        cursor.execute("SELECT id, nom, prenom, club, nation FROM arbitres WHERE id_compete = %s", (self.competition_id,))
        for row in cursor:
            self.arbitres_liststore.append(list(row))
        cursor.close()

    def on_add_arbitre(self, widget):
        dialog = ArbitreDialog(self, "Ajouter un arbitre", self.connection, self.competition_id)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO arbitres (nom, prenom, club, nation, id_compete) VALUES (%s, %s, %s, %s, %s)",
                (data['nom'], data['prenom'], data['club'], data['nation'], self.competition_id)
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
            dialog = ArbitreDialog(self, "Modifier un arbitre", self.connection, self.competition_id, model[treeiter])
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
    def __init__(self, parent, title, connection, competition_id, joueur=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.connection = connection
        self.competition_id = competition_id
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
    def __init__(self, parent, title, connection, competition=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.connection = connection
        self.set_default_size(200, 200)

        box = self.get_content_area()

        self.type_combo = Gtk.ComboBoxText()
        self.type_combo.append_text("classique")
        self.type_combo.append_text("division")
        box.add(Gtk.Label(label="Type de Compétition"))
        box.add(self.type_combo)

        self.formule_entry = Gtk.Entry()
        self.formule_entry.set_placeholder_text("Formule")
        box.add(self.formule_entry)

        self.date_inscription_calendar = Gtk.Calendar()
        self.date_competition_calendar = Gtk.Calendar()
        
        today = datetime.date.today()
        self.date_inscription_calendar.select_day(today.day)
        self.date_inscription_calendar.select_month(today.month - 1, today.year)
        self.date_competition_calendar.select_day(today.day)
        self.date_competition_calendar.select_month(today.month - 1, today.year)
        
        box.add(Gtk.Label(label="Date d'Inscription"))
        box.add(self.date_inscription_calendar)
        
        box.add(Gtk.Label(label="Date de Compétition"))
        box.add(self.date_competition_calendar)

        if competition:
            self.type_combo.set_active_id(competition[1])
            self.formule_entry.set_text(competition[2])
            date_inscription = datetime.datetime.strptime(competition[3], "%Y-%m-%d")
            self.date_inscription_calendar.select_day(date_inscription.day)
            self.date_inscription_calendar.select_month(date_inscription.month - 1, date_inscription.year)
            date_competition = datetime.datetime.strptime(competition[4], "%Y-%m-%d")
            self.date_competition_calendar.select_day(date_competition.day)
            self.date_competition_calendar.select_month(date_competition.month - 1, date_competition.year)

        self.show_all()

    def get_data(self):
        date_inscription = self.date_inscription_calendar.get_date()
        date_competition = self.date_competition_calendar.get_date()
        return {
            'type_de_competition': self.type_combo.get_active_text(),
            'formule': self.formule_entry.get_text(),
            'date_inscription': f"{date_inscription[0]}-{date_inscription[1] + 1:02d}-{date_inscription[2]:02d}",
            'date_competition': f"{date_competition[0]}-{date_competition[1] + 1:02d}-{date_competition[2]:02d}"
        }

class ArbitreDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, competition_id, arbitre=None):
        Gtk.Dialog.__init__(self, title, parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.connection = connection
        self.competition_id = competition_id
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

        self.nation_combo = Gtk.ComboBoxText()
        self.load_countries()
        box.add(self.nation_combo)

        if arbitre:
            self.nom_entry.set_text(arbitre[1])
            self.prenom_entry.set_text(arbitre[2])
            self.club_entry.set_text(arbitre[3])
            self.nation_combo.set_active_id(arbitre[4])

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
            'nation': self.nation_combo.get_active_text()
        }

win = DatabaseManager()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
