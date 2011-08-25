import wx
import sqlite3
import webbrowser


class frMain (wx.Frame):
    """ Frame principal en donde coloco el campo de texto, un boton
        y dos combos, para categoria y subcategoria"""
    def __init__(self, parent):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"TermWebSearch", pos = wx.DefaultPosition, size = wx.Size( 410,110 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        self.edBusca = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        bSizer1.Add( self.edBusca, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.btBucar = wx.Button( self.m_panel1, wx.ID_ANY, u"Buscar", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.btBucar, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.m_panel1.SetSizer( bSizer1 )
        self.m_panel1.Layout()
        bSizer1.Fit( self.m_panel1 )
        bSizer4.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 1 )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        cb_catChoices = []
        self.cb_cat = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, cb_catChoices, wx.CB_DROPDOWN|wx.CB_READONLY|wx.CB_SIMPLE )
        bSizer3.Add( self.cb_cat, 0, wx.ALL, 5 )

        cb_subcatChoices = []
        self.cb_subcat = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, cb_subcatChoices, wx.CB_READONLY )
        bSizer3.Add( self.cb_subcat, 0, wx.ALL, 5 )

        self.m_panel2.SetSizer( bSizer3 )
        self.m_panel2.Layout()
        bSizer3.Fit( self.m_panel2 )
        bSizer4.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 1 )

        """ Eventos"""
        self.cb_cat.Bind(wx.EVT_COMBOBOX, self.cb_cat_change)
        self.btBucar.Bind(wx.EVT_BUTTON, self.bt_click)

        self.SetSizer( bSizer4 )
        self.Layout()

        self.Centre( wx.BOTH )

    def cb_cat_change( self, event ):
        term.load_subcategory()

    def bt_click( self, event ):
        term.load_sites()
        term.open_sites()

class termsearch():
    categories = []
    subcategories = []
    sites = []

    def __init__(self, db, frame):
        self.db = db
        self.frame = frame
        self.load_combos()

    def load_combos(self):
        """ Carga el combo de Categoria y Subcategoria
            Al segundo debe dejarle un lugar vacio"""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM categories')
        self.categories = cursor.fetchall()

        for category in self.categories:
            self.frame.cb_cat.Append(category[1])

        self.frame.cb_cat.SetSelection(0)
        self.load_subcategory()

    def load_subcategory(self):
        """ Carga las subcategorias. de acuerdo a la categoria
            que aparezca en el primero de los combos """
        cursor = self.db.cursor()

        sql = """SELECT sub.* FROM subcategories sub
                 INNER JOIN categories cat ON cat.id_cat = sub.id_cat
                 WHERE cat.nombre LIKE '%s'"""

        cursor.execute(sql % self.frame.cb_cat.Value)
        self.subcategories = cursor.fetchall()

        # Limpia combobox
        self.frame.cb_subcat.Clear()
        # Primero agrega un campo vacio
        self.frame.cb_subcat.Append("")
        # Despues carga las subcategorias
        for subcategory in self.subcategories:
            self.frame.cb_subcat.Append(subcategory[2])

    def load_sites(self):
        cursor = self.db.cursor()
        cat = self.frame.cb_cat.Value

        if self.frame.cb_cat.Value == "":
            subcat = "%"
        else:
            subcat = self.frame.cb_subcat.Value

        sql = """SELECT s.url FROM sites s
                 INNER JOIN subcategories sub ON sub.id_subcat = s.id_subcat
                 INNER JOIN categories cat ON cat.id_cat = sub.id_cat
                 WHERE cat.nombre LIKE '%s' and sub.nombre LIKE '%s'"""

        cursor.execute(sql % (cat, subcat))
        self.sites = cursor.fetchall()

    def open_sites(self):
        text = self.frame.edBusca.Value
        for site in self.sites:
            url = site[0].replace('{text}', text)
            webbrowser.open_new(url)


def paste(frame):
    """ Pega en el campo de texto el valor
        Se modifica la funcion para que no busque en el clipboard lo que se
        tiene copiado, sino via X11 (solo Linux) toma lo seleccionado """
    wx.TheClipboard.UsePrimarySelection(True)
    if not wx.TheClipboard.IsOpened():
        wx.TheClipboard.Open()
        do = wx.TextDataObject()
        success = wx.TheClipboard.GetData(do)
        wx.TheClipboard.Close()
        if success:
            frame.edBusca.SetValue(do.GetText())

def main():
    global term
    app = wx.PySimpleApp()
    frmain = frMain(None)
    db = sqlite3.connect('terms.sqlite')

    term = termsearch(db, frmain)

    paste(frmain)

    frmain.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()




