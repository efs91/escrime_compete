import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import mysql.connector
import datetime
import json

class DatabaseManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ModulComp : Logiciel de compétition modulaire")
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
        self.create_formules_page()
        self.create_tours_page()

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

    def create_formules_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Formules"))

        self.formules_liststore = Gtk.ListStore(int, str, str)  # ID, Nom, Tours
        self.formules_treeview = Gtk.TreeView(model=self.formules_liststore)

        for i, column_title in enumerate(["ID", "Nom", "Tours"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.formules_treeview.append_column(column)

        vbox.pack_start(self.formules_treeview, True, True, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(button_box, False, False, 0)

        add_button = Gtk.Button(label="Ajouter")
        add_button.connect("clicked", self.on_add_formule)
        button_box.pack_start(add_button, True, True, 0)

        edit_button = Gtk.Button(label="Modifier")
        edit_button.connect("clicked", self.on_edit_formule)
        button_box.pack_start(edit_button, True, True, 0)

        delete_button = Gtk.Button(label="Supprimer")
        delete_button.connect("clicked", self.on_delete_formule)
        button_box.pack_start(delete_button, True, True, 0)

        self.load_formules_data()

    def create_tours_page(self):
        vbox = Gtk.VBox()
        self.notebook.append_page(vbox, Gtk.Label(label="Tours"))

        self.tours_liststore = Gtk.ListStore(int, str, str, str, str, str, str, str, str)
        self.tours_treeview = Gtk.TreeView(model=self.tours_liststore)

        for i, column_title in enumerate(["ID", "Nom", "Type", "Nombre de Joueurs", "Joueurs en Mouvement", "Classement", "Poules", "Nombre de Points", "Temps"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.tours_treeview.append_column(column)

        vbox.pack_start(self.tours_treeview, True, True, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(button_box, False, False, 0)

        add_button = Gtk.Button(label="Ajouter")
        add_button.connect("clicked", self.on_add_tour)
        button_box.pack_start(add_button, True, True, 0)

        edit_button = Gtk.Button(label="Modifier")
        edit_button.connect("clicked", self.on_edit_tour)
        button_box.pack_start(edit_button, True, True, 0)

        delete_button = Gtk.Button(label="Supprimer")
        delete_button.connect("clicked", self.on_delete_tour)
        button_box.pack_start(delete_button, True, True, 0)

        self.load_tours_data()

    def load_competitions_data(self):
        self.competitions_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, type_de_competition, formule, date_inscription, date_competition FROM competition")
        for row in cursor:
            row = list(row)
            for i, value in enumerate(row):
                if isinstance(value, datetime.date):
                    row[i] = value.strftime('%Y-%m-%d')
            self.competitions_liststore.append(row)
        cursor.close()

    def load_formules_data(self):
        self.formules_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom, tours FROM formules")
        for row in cursor:
            self.formules_liststore.append(list(row))
        cursor.close()

    def load_tours_data(self):
        self.tours_liststore.clear()
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT t.id, t.nom, tt.nom, t.nb_joueurs, t.joueurs_move, t.classement, t.poules, t.nb_points, t.temps 
            FROM tours t
            JOIN tour_type tt ON t.type = tt.id
        """)
        for row in cursor:
            row = [
                row[0],  # id
                row[1],  # nom
                row[2],  # type name
                str(row[3]) if row[3] is not None else '',  # nb_joueurs
                str(row[4]) if row[4] is not None else '',  # joueurs_move
                row[5] if row[5] is not None else '',  # classement
                row[6] if row[6] is not None else '',  # poules
                str(row[7]) if row[7] is not None else '',  # nb_points
                str(row[8]) if row[8] is not None else ''  # temps
            ]
            self.tours_liststore.append(row)
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
   
    def on_add_formule(self, widget):
        dialog = FormuleDialog(self, "Ajouter une formule", self.connection)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO formules (nom, tours) VALUES (%s, %s)",
                (data['nom'], data['tours'])
            )
            self.connection.commit()
            cursor.close()
            self.load_formules_data()

        dialog.destroy()

    def on_edit_formule(self, widget):
        selection = self.formules_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            formule_id = model[treeiter][0]
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nom, tours FROM formules WHERE id = %s", (formule_id,))
            formule_data = cursor.fetchone()
            cursor.close()
            if formule_data:
                dialog = FormuleDialog(self, "Modifier une formule", self.connection, formule_data)
                response = dialog.run()

                if response == Gtk.ResponseType.OK:
                    data = dialog.get_data()
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "UPDATE formules SET nom=%s, tours=%s WHERE id=%s",
                        (data['nom'], data['tours'], formule_id)
                    )
                    self.connection.commit()
                    cursor.close()
                    self.load_formules_data()

                dialog.destroy()



    def on_delete_formule(self, widget):
        selection = self.formules_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            formule_id = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Êtes-vous sûr de vouloir supprimer cette formule ?",
            )
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM formules WHERE id=%s", (formule_id,))
                self.connection.commit()
                cursor.close()
                self.load_formules_data()
            dialog.destroy()

    def on_edit_tour(self, widget):
        selection = self.tours_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            tour_data = list(model[treeiter])
            tour_id = tour_data[0]
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nom, type, nb_joueurs, joueurs_move, classement, poules, nb_points, temps FROM tours WHERE id = %s", (tour_id,))
            tour = cursor.fetchone()
            cursor.close()
            dialog = TourDialog(self, "Modifier un tour", self.connection, tour)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE tours SET nom=%s, type=%s, nb_joueurs=%s, joueurs_move=%s, classement=%s, poules=%s, nb_points=%s, temps=%s WHERE id=%s",
                    (data['nom'], data['type'], data['nb_joueurs'], data['joueurs_move'], data['classement'], data['poules'], data['nb_points'], data['temps'], tour_id)
                )
                self.connection.commit()
                cursor.close()
                self.load_tours_data()

            dialog.destroy()

    def on_add_tour(self, widget):
        dialog = TourDialog(self, "Ajouter un tour", self.connection)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO tours (nom, type, nb_joueurs, joueurs_move, classement, poules, nb_points, temps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (data['nom'], data['type'], data['nb_joueurs'], data['joueurs_move'], data['classement'], data['poules'], data['nb_points'], data['temps'])
            )
            self.connection.commit()
            cursor.close()
            self.load_tours_data()

        dialog.destroy()

    def on_delete_tour(self, widget):
        selection = self.tours_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            tour_id = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Êtes-vous sûr de vouloir supprimer ce tour ?",
            )
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM tours WHERE id=%s", (tour_id,))
                self.connection.commit()
                cursor.close()
                self.load_tours_data()
            dialog.destroy()

class CompetitionDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, competition=None):
        Gtk.Dialog.__init__(self, title, parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.connection = connection
        self.set_default_size(300, 200)

        box = self.get_content_area()

        self.add_labeled_entry(box, "Type de Compétition", "type_de_competition")
        self.add_labeled_entry(box, "Formule", "formule")
        self.add_labeled_entry(box, "Date d'Inscription", "date_inscription")
        self.add_labeled_entry(box, "Date de Compétition", "date_competition")

        self.show_all()

        if competition:
            self.type_de_competition_entry.set_text(competition[1])
            self.formule_entry.set_text(competition[2])
            self.date_inscription_entry.set_text(competition[3])
            self.date_competition_entry.set_text(competition[4])

    def add_labeled_entry(self, box, label_text, entry_name):
        label = Gtk.Label(label=label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(label_text)
        setattr(self, f"{entry_name}_label", label)
        setattr(self, f"{entry_name}_entry", entry)
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

    def get_data(self):
        return {
            'type_de_competition': self.type_de_competition_entry.get_text(),
            'formule': self.formule_entry.get_text(),
            'date_inscription': self.date_inscription_entry.get_text(),
            'date_competition': self.date_competition_entry.get_text()
        }





class FormuleDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, formule=None):
        Gtk.Dialog.__init__(self, title, parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.connection = connection
        self.set_default_size(300, 400)

        self.tours = []
        if formule:
            self.tours = json.loads(formule[2]) if formule[2] else []

        box = self.get_content_area()

        self.add_labeled_entry(box, "Nom", "nom")

        self.tour_combo = Gtk.ComboBoxText()
        self.load_tours()
        box.pack_start(Gtk.Label(label="Sélectionner un tour"), False, False, 0)
        box.pack_start(self.tour_combo, False, False, 0)

        self.add_tour_button = Gtk.Button(label="Ajouter un tour")
        self.add_tour_button.connect("clicked", self.on_add_tour)
        box.pack_start(self.add_tour_button, False, False, 0)

        self.selected_tours_liststore = Gtk.ListStore(str)
        self.selected_tours_treeview = Gtk.TreeView(model=self.selected_tours_liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tours sélectionnés", renderer, text=0)
        self.selected_tours_treeview.append_column(column)
        box.pack_start(self.selected_tours_treeview, True, True, 0)

        self.delete_tour_button = Gtk.Button(label="Supprimer le tour")
        self.delete_tour_button.connect("clicked", self.on_delete_tour)
        box.pack_start(self.delete_tour_button, False, False, 0)

        self.show_all()

        if formule:
            self.nom_entry.set_text(formule[1])
            self.load_selected_tours()

    def add_labeled_entry(self, box, label_text, entry_name):
        label = Gtk.Label(label=label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(label_text)
        setattr(self, f"{entry_name}_label", label)
        setattr(self, f"{entry_name}_entry", entry)
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

    def load_tours(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom FROM tours ORDER BY nom")
        for row in cursor:
            self.tour_combo.append_text(f"{row[1]} (ID: {row[0]})")
        cursor.close()
        self.tour_combo.set_active(0)

    def load_selected_tours(self):
        self.selected_tours_liststore.clear()
        for tour in self.tours:
            self.selected_tours_liststore.append([tour])

    def on_add_tour(self, widget):
        active_text = self.tour_combo.get_active_text()
        if active_text:
            self.tours.append(active_text)
            self.selected_tours_liststore.append([active_text])

    def on_delete_tour(self, widget):
        selection = self.selected_tours_treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            tour = model[treeiter][0]
            self.tours.remove(tour)
            model.remove(treeiter)

    def get_data(self):
        return {
            'nom': self.nom_entry.get_text(),
            'tours': json.dumps(self.tours)
        }


class TourDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, tour=None):
        Gtk.Dialog.__init__(self, title, parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.connection = connection
        self.set_default_size(300, 350)  # Augmenter la taille pour accueillir les nouveaux champs

        box = self.get_content_area()

        self.nom_entry = Gtk.Entry()
        self.nom_entry.set_placeholder_text("Nom")
        nom_label = Gtk.Label(label="Nom")
        box.pack_start(nom_label, False, False, 0)
        box.pack_start(self.nom_entry, False, False, 0)

        self.type_combo = Gtk.ComboBoxText()
        self.type_ids = []  # Liste pour stocker les IDs des types de tours
        self.load_tour_types()
        type_label = Gtk.Label(label="Type")
        box.pack_start(type_label, False, False, 0)
        box.pack_start(self.type_combo, False, False, 0)

        self.add_labeled_entry(box, "Nombre de Joueurs", "nb_joueurs")
        self.add_labeled_entry(box, "Joueurs en Mouvement", "joueurs_move")
        self.add_labeled_entry(box, "Classement", "classement")
        self.add_labeled_entry(box, "Poules", "poules")
        self.add_labeled_entry(box, "Nombre de Points", "nb_points")
        self.add_labeled_entry(box, "Temps", "temps")

        self.type_combo.connect("changed", self.on_type_changed)

        self.show_all()

        if tour:
            self.nom_entry.set_text(tour[1] if tour[1] is not None else "")
            tour_type_id = int(tour[2])
            self.set_active_id_in_combo(tour_type_id)
            self.nb_joueurs_entry.set_text(str(tour[3]) if tour[3] is not None else "")
            self.joueurs_move_entry.set_text(str(tour[4]) if tour[4] is not None else "")
            self.classement_entry.set_text(tour[5] if tour[5] is not None else "")
            self.poules_entry.set_text(tour[6] if tour[6] is not None else "")
            self.nb_points_entry.set_text(str(tour[7]) if tour[7] is not None else "")
            self.temps_entry.set_text(str(tour[8]) if tour[8] is not None else "")
            self.update_visibility(tour_type_id)  # Mettre à jour la visibilité des champs après avoir défini la sélection initiale
        else:
            self.set_active_id_in_combo(1)
            self.update_visibility(1)  # ID 1 par défaut

    def add_labeled_entry(self, box, label_text, entry_name):
        label = Gtk.Label(label=label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(label_text)
        setattr(self, f"{entry_name}_label", label)
        setattr(self, f"{entry_name}_entry", entry)
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

    def load_tour_types(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nom FROM tour_type ORDER BY nom")
        for row in cursor:
            self.type_ids.append(row[0])  # Stocker l'ID
            self.type_combo.append_text(row[1])
        cursor.close()

    def on_type_changed(self, combo=None):
        type_id = self.get_selected_type_id()
        self.update_visibility(type_id)

    def update_visibility(self, type_id):
        # Initialement masquer tous les champs sauf "nom"
        self.joueurs_move_entry.set_visible(False)
        self.classement_entry.set_visible(False)
        self.poules_entry.set_visible(False)
        self.nb_joueurs_entry.set_visible(False)
        self.nb_points_entry.set_visible(False)
        self.temps_entry.set_visible(False)
        self.joueurs_move_label.set_visible(False)
        self.classement_label.set_visible(False)
        self.poules_label.set_visible(False)
        self.nb_joueurs_label.set_visible(False)
        self.nb_points_label.set_visible(False)
        self.temps_label.set_visible(False)
        
        # Afficher les champs en fonction du type_id
        if type_id in [1, 2, 4, 5, 6, 7, 8]:
            self.nb_joueurs_entry.set_visible(True)
            self.nb_points_entry.set_visible(True)
            self.temps_entry.set_visible(True)
            self.nb_joueurs_label.set_visible(True)
            self.nb_points_label.set_visible(True)
            self.temps_label.set_visible(True)
        elif type_id == 3:
            self.joueurs_move_entry.set_visible(True)
            self.nb_joueurs_entry.set_visible(True)
            self.nb_points_entry.set_visible(True)
            self.temps_entry.set_visible(True)
            self.joueurs_move_label.set_visible(True)
            self.nb_joueurs_label.set_visible(True)
            self.nb_points_label.set_visible(True)
            self.temps_label.set_visible(True)

    def set_active_text_in_combo(self, combo, text):
        """Helper function to set active text in Gtk.ComboBoxText."""
        model = combo.get_model()
        for i, row in enumerate(model):
            if row[0] == text:
                combo.set_active(i)
                break

    def set_active_id_in_combo(self, id):
        """Helper function to set active ID in Gtk.ComboBoxText."""
        if id in self.type_ids:
            active_index = self.type_ids.index(id)
            self.type_combo.set_active(active_index)

    def get_selected_type_id(self):
        active_index = self.type_combo.get_active()
        if active_index != -1:
            return self.type_ids[active_index]
        return None

    def get_data(self):
        return {
            'nom': self.nom_entry.get_text() if self.nom_entry.get_text() else None,
            'type': self.get_selected_type_id(),
            'nb_joueurs': int(self.nb_joueurs_entry.get_text()) if self.nb_joueurs_entry.get_text() else None,
            'joueurs_move': int(self.joueurs_move_entry.get_text()) if self.joueurs_move_entry.get_text() else None,
            'classement': self.classement_entry.get_text() if self.classement_entry.get_text() else None,
            'poules': self.poules_entry.get_text() if self.poules_entry.get_text() else None,
            'nb_points': int(self.nb_points_entry.get_text()) if self.nb_points_entry.get_text() else None,
            'temps': int(self.temps_entry.get_text()) if self.temps_entry.get_text() else None
        }





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
        cursor.execute("SELECT id, nom, prenom FROM joueurs WHERE id_compete = %s", (self.competition_id,))
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
            joueur_data = list(model[treeiter])
            dialog = JoueurDialog(self, "Modifier un joueur", self.connection, self.competition_id, joueur_data)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE joueurs SET nom=%s, prenom=%s, club=%s, sexe=%s, nation=%s, classement=%s WHERE id=%s",
                    (data['nom'], data['prenom'], data['club'], data['sexe'], data['nation'], data['classement'], joueur_data[0])
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
            arbitre_data = list(model[treeiter])
            dialog = ArbitreDialog(self, "Modifier un arbitre", self.connection, self.competition_id, arbitre_data)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                data = dialog.get_data()
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE arbitres SET nom=%s, prenom=%s, club=%s, nation=%s WHERE id=%s",
                    (data['nom'], data['prenom'], data['club'], data['nation'], arbitre_data[0])
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
        Gtk.Dialog.__init__(self, title, parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.connection = connection
        self.competition_id = competition_id
        self.set_default_size(300, 200)

        box = self.get_content_area()

        self.add_labeled_entry(box, "Nom", "nom")
        self.add_labeled_entry(box, "Prénom", "prenom")
        self.add_labeled_entry(box, "Club", "club")

        self.sexe_combo = Gtk.ComboBoxText()
        self.sexe_combo.append_text("F")
        self.sexe_combo.append_text("M")
        self.sexe_combo.set_active(0)
        box.pack_start(Gtk.Label(label="Sexe"), False, False, 0)
        box.pack_start(self.sexe_combo, False, False, 0)

        self.nation_combo = Gtk.ComboBoxText()
        self.load_countries()
        box.pack_start(Gtk.Label(label="Nation"), False, False, 0)
        box.pack_start(self.nation_combo, False, False, 0)

        self.add_labeled_entry(box, "Classement", "classement")

        self.show_all()

        if joueur:
            self.nom_entry.set_text(joueur[1])
            self.prenom_entry.set_text(joueur[2])
            self.club_entry.set_text(joueur[3])
            self.set_active_text_in_combo(self.sexe_combo, joueur[4])
            self.set_active_text_in_combo(self.nation_combo, joueur[5])
            self.classement_entry.set_text(str(joueur[6]))

    def add_labeled_entry(self, box, label_text, entry_name):
        label = Gtk.Label(label=label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(label_text)
        setattr(self, f"{entry_name}_label", label)
        setattr(self, f"{entry_name}_entry", entry)
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

    def load_countries(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM countries ORDER BY name")
        for row in cursor:
            self.nation_combo.append_text(row[0])
        cursor.close()
        self.nation_combo.set_active(0)
        for i, country in enumerate(self.nation_combo.get_model()):
            if country[0] == "France":
                self.nation_combo.set_active(i)
                break

    def set_active_text_in_combo(self, combo, text):
        model = combo.get_model()
        for i, row in enumerate(model):
            if row[0] == text:
                combo.set_active(i)
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

class ArbitreDialog(Gtk.Dialog):
    def __init__(self, parent, title, connection, competition_id, arbitre=None):
        Gtk.Dialog.__init__(self, title, parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.connection = connection
        self.competition_id = competition_id
        self.set_default_size(300, 200)

        box = self.get_content_area()

        self.add_labeled_entry(box, "Nom", "nom")
        self.add_labeled_entry(box, "Prénom", "prenom")
        self.add_labeled_entry(box, "Club", "club")

        self.nation_combo = Gtk.ComboBoxText()
        self.load_countries()
        box.pack_start(Gtk.Label(label="Nation"), False, False, 0)
        box.pack_start(self.nation_combo, False, False, 0)

        self.show_all()

        if arbitre:
            self.nom_entry.set_text(arbitre[1])
            self.prenom_entry.set_text(arbitre[2])
            self.club_entry.set_text(arbitre[3])
            self.set_active_text_in_combo(self.nation_combo, arbitre[4])

    def add_labeled_entry(self, box, label_text, entry_name):
        label = Gtk.Label(label=label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(label_text)
        setattr(self, f"{entry_name}_label", label)
        setattr(self, f"{entry_name}_entry", entry)
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

    def load_countries(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM countries ORDER BY name")
        for row in cursor:
            self.nation_combo.append_text(row[0])
        cursor.close()
        self.nation_combo.set_active(0)
        for i, country in enumerate(self.nation_combo.get_model()):
            if country[0] == "France":
                self.nation_combo.set_active(i)
                break

    def set_active_text_in_combo(self, combo, text):
        model = combo.get_model()
        for i, row in enumerate(model):
            if row[0] == text:
                combo.set_active(i)
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
