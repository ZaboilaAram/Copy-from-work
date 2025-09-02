import os
import sys
from random import randint
from colorsys import hsv_to_rgb
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal


# Node.py
class Node:
    '''A Node in a tree with an arbitrary number of children (an arbitrary
    branching factor).'''

    def __init__(self):
        '''Create a new node with an empty list of children.'''
        self.children = []

    def add(self, node):
        '''Append node as a child to the parent self.'''
        self.children.append(node)

    def getChildren(self):
        '''Return the list of children of the parent self.'''
        return self.children


# DirNode.py
class DirNode(Node):
    '''DirNode extends the Node class. It creates a DirNode which represents
    a directory's attributes within a filesystem such as directory path and
    size.'''

    def __init__(self, path, size):
        '''Create a new DirNode with an empty list of children and attributes
        specified by the parameters.'''
        super(DirNode, self).__init__()
        self.path = path            # The location of the file
        self.size = size            # The size of the file (in KB)

    def getPath(self):
        '''Return the path of the DirNode self.'''
        return self.path

    def getSize(self):
        '''Return the size of the DirNode self.'''
        return self.size

    def setSize(self, size):
        '''Set the size of the DirNode self.'''
        self.size = size


# FileNode.py
class FileNode(Node):
    '''FileNode extends the Node class. It create a FileNode which represents
    a file's attributes within a filesystem such as the filepath and size. It
    also contains the following visual representation data: gradient colours
    and mouse hover colours.'''

    def __init__(self, path, size):
        '''Create a new FileNode with an empty list of children and attributes
        specified by the parameters.'''
        super(FileNode, self).__init__()
        self.path = path            # The location of the file
        self.size = size            # The size of the file (in KB)
        self.tColour = None         # The top colour of the gradient
        self.bColour = None         # The bottom colour of the gradient
        self.hColour = None         # The mouse hover colour
        # Set the colours for the FileNode
        self.__setRandomColours()

    def __setRandomColours(self):
        '''Set the gradient and mouse hover colours using an aesthetically
        pleasing HSV colour palette. The same hue value is used for all colours
        with varying degrees of saturation to generate different shades.'''
        hue = randint(0, 360) / 360
        self.tColour = tuple(i * 255 for i in hsv_to_rgb(hue, 0.6, 0.95))
        self.bColour = tuple(i * 255 for i in hsv_to_rgb(hue, 1, 0.95))
        self.hColour = tuple(i * 255 for i in hsv_to_rgb(hue, 0.05, 0.95))

    def getPath(self):
        '''Return the path of the FileNode self.'''
        return self.path

    def getSize(self):
        '''Return the size of the FileNode self.'''
        return self.size

    def getTColour(self):
        '''Return the top colour of the FileNode self.'''
        return self.tColour

    def getBColour(self):
        '''Return the bottom colour of the FileNode self.'''
        return self.bColour

    def getHColour(self):
        '''Return the mouse hover colour of the FileNode self.'''
        return self.hColour


# TreemapBuilderThread - Thread pentru construirea treemap-ului
class TreemapBuilderThread(QThread):
    '''Thread pentru construirea treemap-ului cu progress reporting.'''
    
    progress = pyqtSignal(int)  # Signal pentru progres (0-100)
    finished_build = pyqtSignal(object)  # Signal pentru treemap finalizat
    status_update = pyqtSignal(str)  # Signal pentru actualizarea statusului
    
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.total_items = 0
        self.processed_items = 0
    
    def run(self):
        '''Rulează construirea treemap-ului în thread separat.'''
        try:
            self.status_update.emit("Scanning directory structure...")
            self.progress.emit(0)
            
            # Primul pas: numărăm total items pentru progres
            self.total_items = self._countItems(self.directory)
            self.processed_items = 0
            
            self.status_update.emit("Building treemap...")
            
            # Al doilea pas: construim treemap-ul
            treemap = Treemap()
            treemap.root = self._buildTree(self.directory)
            
            self.progress.emit(100)
            self.status_update.emit("Treemap completed!")
            self.finished_build.emit(treemap)
            
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
            self.finished_build.emit(None)
    
    def _countItems(self, path):
        '''Numără total items pentru calcul progres.'''
        count = 0
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                count += 1
                if os.path.isdir(item_path):
                    try:
                        count += self._countItems(item_path)
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return count
    
    def _buildTree(self, path):
        '''Construiește recursiv structura de arbore din filesystem.'''
        total_size = 0
        dir_node = DirNode(path, 0)
        
        try:
            for item in os.listdir(path):
                self.processed_items += 1
                progress_percent = int((self.processed_items / max(self.total_items, 1)) * 100)
                self.progress.emit(progress_percent)
                
                item_path = os.path.join(path, item)
                
                if os.path.isfile(item_path):
                    try:
                        size = os.path.getsize(item_path) / 1024  # Size in KB
                        file_node = FileNode(item_path, size)
                        dir_node.add(file_node)
                        total_size += size
                    except OSError:
                        continue
                        
                elif os.path.isdir(item_path):
                    try:
                        sub_dir = self._buildTree(item_path)
                        if sub_dir and sub_dir.getSize() > 0:
                            dir_node.add(sub_dir)
                            total_size += sub_dir.getSize()
                    except (OSError, PermissionError):
                        continue
                        
        except (OSError, PermissionError):
            pass
            
        dir_node.setSize(total_size)
        return dir_node


# Treemap class
class Treemap:
    '''Treemap class for building filesystem visualization.'''
    
    def __init__(self):
        self.root = None
    
    def getRoot(self):
        '''Return the root node of the treemap.'''
        return self.root


# GUIWindow.py
class GUIWindow(QtWidgets.QMainWindow):
    '''GUIWindow the extends the QtWidgets.QMainWindow class. It creates a
    basic window that contains a MenuBar and a StatusBar, both of which are
    modifiable. The window includes advanced functionality such as appearing in
    the center of the screen binding of key and mouse events.'''

    def __init__(self, winTitle, winWidth, winHeight, winIcon=None):
        '''Create a new GUIWindow with a specific window title, width, height
        and window icon.'''
        super(GUIWindow, self).__init__()
        # Exceptions
        self.__menuExistsException = Exception(
            'The specified menu already exists!')
        self.__menuNotFoundException = Exception(
            'The specified menu was not found!')
        # GUIWindow variables
        self.__menubar = self.menuBar()         # Menu Bar
        self.__menuDict = {}                    # Map of Menus for Menubar
        self.__statusLabel = QtWidgets.QLabel()  # New Status label
        self.__keyInputDict = {}                # Map of key events
        self.__checkableActions = {}            # Map of checkable QActions
        self.__mouseMoveEvents = []             # List of mouse move events
        self.__mouseClickEvents = []            # List of mouse click events
        self.__mouseReleaseEvents = []          # List of mouse release events
        
        # Progress bar pentru colțul din dreapta jos
        self.__progressBar = QtWidgets.QProgressBar()
        self.__progressBar.setVisible(False)
        self.__progressBar.setFixedSize(200, 20)
        
        # Configure the window's properties
        self.setGeometry(0, 0, winWidth, winHeight)
        self.setMinimumSize(int(winWidth / 2), int(winHeight / 2))
        self.setWindowTitle(winTitle)
        if winIcon:  # Only set icon if provided
            self.setWindowIcon(QtGui.QIcon(winIcon))
        
        # Bind the QLabel și progress bar to the Status Bar
        self.statusBar().addWidget(self.__statusLabel, 1)
        self.statusBar().addPermanentWidget(self.__progressBar)
        
        # Set the window to appear in the center of the screen
        self.__centerOnScreen()

    def showProgressBar(self):
        '''Afișează progress bar-ul.'''
        self.__progressBar.setVisible(True)
        self.__progressBar.setValue(0)
    
    def hideProgressBar(self):
        '''Ascunde progress bar-ul.'''
        self.__progressBar.setVisible(False)
    
    def updateProgressBar(self, value):
        '''Actualizează valoarea progress bar-ului.'''
        self.__progressBar.setValue(value)

    def keyPressEvent(self, event):
        '''Handle and process all key press events.'''
        eventKey = event.key()
        if eventKey in self.__keyInputDict:
            self.__keyInputDict[eventKey][0]()

    def keyReleaseEvent(self, event):
        '''Handle and process all key release events.'''
        eventKey = event.key()
        if eventKey in self.__keyInputDict:
            self.__keyInputDict[eventKey][1]()

    def mouseMoveEvent(self, event):
        '''Handle and process all mouse movement events.'''
        for func in self.__mouseMoveEvents:
            func(event)

    def mousePressEvent(self, event):
        '''Handle and process all mouse click events.'''
        for func in self.__mouseClickEvents:
            func(event)

    def mouseReleaseEvent(self, event):
        '''Handle and process all mouse release events.'''
        for func in self.__mouseReleaseEvents:
            func(event)

    def __centerOnScreen(self):
        '''Move the position of the window so that it is positioned perfectly
        in the center of the screen.'''
        res = QtWidgets.QDesktopWidget().screenGeometry()
        move_width = (res.width() / 2) - (self.frameSize().width() / 2)
        move_height = (res.height() / 2) - (self.frameSize().height() / 2)
        self.move(int(move_width), int(move_height))

    def updateMouseEvents(self, moveEvents, clickEvents, releaseEvents):
        '''Update the mouse event lists for movement, clicking and releasing as
        specified by the events in the lists from the parameters.'''
        self.__mouseMoveEvents = moveEvents
        self.__mouseClickEvents = clickEvents
        self.__mouseReleaseEvents = releaseEvents

    def updateKeyBindings(self, keyBindings):
        '''Change the current value of the keys and their events for keypress
        and keyrelease to the ones specified by keyBindings.'''
        self.__keyInputDict = keyBindings.copy()

    def setStatusBar(self, statusText):
        '''Change the current value of the StatusBar's text.'''
        self.__statusLabel.setText(statusText)

    def addMenu(self, menuTitle):
        '''Add a new menu with a title specified by menuTitle to the window's
        MenuBar.'''
        # Check if menuTitle does not exist (prevent duplicates)
        if menuTitle in self.__menuDict:
            raise self.__menuExistsException
        else:
            self.__menuDict[menuTitle] = \
                self.__menubar.addMenu('&' + menuTitle)

    def addMenuItem(self, menuTitle, menuItemName, evtFunction=None):
        '''Add a new menu item to an existing menu with a title specified by
        menuTitle. Connect an event function to the menu item if the specified
        value is not None.'''
        # Check if menuTitle exists
        if menuTitle in self.__menuDict:
            # Create the menu item
            menuItem = QtWidgets.QAction('&' + menuItemName, self)
            if evtFunction:
                menuItem.triggered.connect(lambda: evtFunction())
            # Add the menu items to the menu item dictionary
            self.__menuDict[menuTitle].addAction(menuItem)
        else:
            raise self.__menuNotFoundException

    def addCheckableMenuItem(self, menuTitle, menuItemName, isChecked,
                             evtFunction=None):
        '''Add a new checkable menu item to an existing menu with a title
        specified by menuTitle. Connect an event function to the checkable menu
        item if the specified value is not None. The checkable menu item is
        checked if the value of isChecked is True, unchecked if False.'''
        # Check if menuTitle exists
        if menuTitle in self.__menuDict:
            # Create the checkable menu item and set the check flag
            menuItem = QtWidgets.QAction(
                '&' + menuItemName, self, checkable=True)
            menuItem.setChecked(isChecked)
            # Store menu action item
            self.__checkableActions[menuItemName] = menuItem
            if evtFunction:
                menuItem.triggered.connect(lambda: evtFunction())
            # Add the menu items to the menu item dictionary
            self.__menuDict[menuTitle].addAction(menuItem)
        else:
            raise self.__menuNotFoundException

    def setCheckedMenuItem(self, menuItem, isChecked):
        '''Set a checkable menu menu item, specified by menuItem to checked
        if isChecked is True, unchecked if False.'''
        # Check if checkable menu item exists
        if menuItem in self.__checkableActions:
            # Set the checked menu item to the value of isChecked
            self.__checkableActions[menuItem].setChecked(isChecked)
        else:
            raise self.__menuNotFoundException

    def addMenuSeperator(self, menuTitle):
        '''Add a seperator item to an existing menu with a title specified by
        menuTitle.'''
        # Check if menuTitle exists
        if menuTitle in self.__menuDict:
            self.__menuDict[menuTitle].addSeparator()
        else:
            raise self.__menuNotFoundException


# TileFrame.py
class TileFrame(QtWidgets.QFrame):
    '''TileFrame extends the QtGui.QFrame class. It is used to render the
    Treemap data structure, each node in the Treemap is rendered as
    rectanglular tiles with a fixed colour or gradient colours. Hovered tiles
    are rendered using a lighter fixed colour.'''

    def __init__(self, parentWindow):
        '''Create a new TileFrame.'''
        super(TileFrame, self).__init__(parentWindow)
        # TileFrame variables
        self.__treemap = None
        self.__isBorders = True
        self.__isGradient = False
        self.__rectNodes = []
        self.__selectedNode = None
        self.__borderCol = QtGui.QColor(0, 0, 0)
        self.__bgCol = QtGui.QColor(64, 64, 64)
        self.__txtCol = QtGui.QColor(38, 38, 38)
        self.__txtFont = QtGui.QFont('CopperBlack', 60, QtGui.QFont.Bold)
        self.__txt = "Visualizer"
        # Set strong policy for focusing keyboard events to Tileframe
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

    def __buildTiles(self, painter, node, size, location):
        '''Render the Treemap Node by Node. Render the DirNode as borders
        with the border colour and render the FileNodes as rectangular tiles.
        Render the FileNodes with gradient colours iff gradients are enabled
        and render with a fixed colour otherwise.'''
        borderRect = QtCore.QRect(int(location[0]),
                                  int(location[1]),
                                  int(size[0]),
                                  int(size[1]))
        # If rendering borders is enabled
        if self.__isBorders:
            # Shift the dimensions of the rectangle
            location[0] += 1
            location[1] += 1
            size[0] -= 2
            size[1] -= 2
        totalSize = max(node.getSize(), 1)  # Prevent ZeroDivisionError
        for item in node.getChildren():
            percent = item.getSize() / totalSize
            itemArea = (size[0] * size[1]) * percent
            # Calculate dimensions of the rectangle
            if size[1] > size[0]:
                width = size[0]
                height = itemArea / width
                # Draw rectangle
                if self.__isGradient:
                    self.__drawGradientRectangle(painter,
                                                 item,
                                                 [width, height],
                                                 location)
                else:
                    self.__drawRectangle(painter,
                                         item,
                                         [width, height],
                                         location)
                location[1] += height
            else:
                height = size[1]
                width = itemArea / height
                # Draw rectangle
                if self.__isGradient:
                    self.__drawGradientRectangle(painter,
                                                 item,
                                                 [width, height],
                                                 location)
                else:
                    self.__drawRectangle(painter,
                                         item,
                                         [width, height],
                                         location)
                location[0] += width
        # If rendering borders is enabled
        if self.__isBorders:
            # Draw the border around the rectangle
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(self.__borderCol)
            painter.drawRect(borderRect)

    def __drawGradientRectangle(self, painter, node, size, location):
        '''Render a Node of type FileNode as a rectangular gradient
        proportional to the size of the file represented by FileNode. Render
        the FileNode with its hover colour iff it's mouse hovered, otherwise
        render the FileNode with the top and bottom gradient colours.'''
        if isinstance(node, FileNode):
            # Obtain the components of a rectangle
            x1 = location[0]
            y1 = location[1]
            x2 = size[0] + 1
            y2 = size[1] + 1
            # Store a map of the file nodes and their display rectangle tiles
            rect = QtCore.QRect(int(x1), int(y1), int(x2), int(y2))
            self.__rectNodes.append((rect, node))
            # Set the top and bottom gradient colours to the Node's hover
            # colours if the file's node is selected, otherwise obtain the top
            # and bottom gradient colours from node
            if self.__selectedNode == node:
                topCol = botCol = node.getHColour()
            else:
                topCol = node.getTColour()
                botCol = node.getBColour()
            # Obtain the components of rectanglular gradient
            gradX1 = location[0]
            gradY1 = location[1] + size[0]
            gradX2 = (location[0] + size[0]) - size[0]
            gradY2 = location[1] + size[1]
            # Render the tile as a gradient
            grad = QtGui.QLinearGradient(gradX1, gradY1, gradX2, gradY2)
            grad.setColorAt(0.0, QtGui.QColor(int(topCol[0]), int(topCol[1]), int(topCol[2])))
            grad.setColorAt(1.0, QtGui.QColor(int(botCol[0]), int(botCol[1]), int(botCol[2])))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(grad))
            painter.drawRect(rect)
        # Recursively render the next tile in the Treemap
        self.__buildTiles(painter, node, size, location[:])

    def __drawRectangle(self, painter, node, size, location):
        '''Render a Node of type FileNode as a rectangular tile proportional to
        the size of file represented by the FileNode. Render the FileNode with
        its hover colour iff it's mouse hovered, otherwise render the FileNode
        with the top gradient colour.'''
        if isinstance(node, FileNode):
            # Obtain the components of a rectangle
            x1 = location[0]
            x2 = location[1]
            y1 = size[0] + 1
            y2 = size[1] + 1
            # Store a map of the file nodes and their display rectangle tiles
            rect = QtCore.QRect(int(x1), int(x2), int(y1), int(y2))
            self.__rectNodes.append((rect, node))
            # Obtain the file's hover colour if it is selected otherwise obtain
            # it's regular top gradient colour
            if self.__selectedNode == node:
                col = node.getHColour()
            else:
                col = node.getTColour()
            painter.fillRect(rect, QtGui.QColor(
                int(col[0]),
                int(col[1]),
                int(col[2])))
        # Recursively render the next tile in the Treemap
        self.__buildTiles(painter, node, size, location[:])

    def getHoveredNodePath(self, mousePos):
        '''Return the path of a file, as a string, from a Node that is mouse
        hovered.'''
        mX = mousePos.x()
        mY = mousePos.y() - self.y()  # Account for location of widget
        # Iterate through all the rectangles
        for item in self.__rectNodes:
            rX = item[0].x()
            rY = item[0].y()
            rW = item[0].width()
            rH = item[0].height()
            if (mX >= rX and mX <= (rX + rW)) and (mY >= rY and mY <= (rY +
                                                                       rH)):
                # Store the hovered node as the selected node and update
                self.__selectedNode = item[1]
                self.update()
                # Return the path of the file represented by the FileNode
                return item[1].getPath()

    def isMapped(self):
        '''Return true if Treemap exists, False otherwise.'''
        return self.__treemap

    def toggleBorders(self):
        '''Enable drawing of borders if drawing borders was dissabled and
        dissable drawing of borders if it was previously enabled.'''
        if self.isMapped():
            # Toggle borders and update the tile rendering
            self.__isBorders = not self.__isBorders
            self.update()

    def toggleGradient(self):
        '''Enable drawing of gradients if drawing gradients was dissabled and
        dissable drawing of gradients if they were previously enabled.'''
        if self.isMapped():
            # Toggle gradient and update the tile rendering
            self.__isGradient = not self.__isGradient
            self.update()

    def screenshot(self, filename):
        '''Obtain a pixel map of the current window and save it as a .PNG
        file with the name specified by filename.'''
        QApplication.primaryScreen().grabWindow(self.winId()).save(filename, 'png')

    def clearMap(self):
        '''Reset the visual map variables and clear the Treemap.'''
        # Reset the toggle variables
        self.__isBorders = True
        self.__isGradient = False
        # Clear the node rectangles
        self.__rectNodes = []
        # Clear the Treemap
        self.__treemap = None

    def setTreemap(self, treemap):
        '''Setează treemap-ul construit.'''
        self.__treemap = treemap
        self.update()

    def paintEvent(self, event):
        '''Handle and process all of the drawing for the Treemap. Render the
        Treemap if it's loaded, otherwise render a grey background with darker
        grey text centered on the window.'''
        self.__rectNodes = []  # Clear all the rectangle node list
        painter = QtGui.QPainter(self)  # Used to draw on the frame
        # Clear all drawings on the TileFrame
        painter.eraseRect(0, 0, self.width(), self.height())
        if self.isMapped():
            # Set the initial conditions and render the Treemap
            size = [self.width(), self.height()]
            location = [0, 0]
            self.__buildTiles(painter,
                              self.__treemap.getRoot(),
                              size,
                              location)
        else:
            # Draw the default background
            painter.fillRect(0, 0, self.width(), self.height(), self.__bgCol)
            # Draw the default text
            painter.setPen(self.__txtCol)
            painter.setFont(self.__txtFont)
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter, self.__txt)


# DiskmapApp.py
class DiskmapApp(QtWidgets.QApplication):
    '''DiskmapApp extends the QtWidgets.QApplication class. This class creates
    the GUI for the Diskmap application and provides functions for all of the
    application's events. It uses TileFrame and GUIWindow to create a window,
    menu, status bar and the frame where the Treemap tiles are rendered.'''

    def __init__(self, args):
        '''Create a new DiskmapApp with arguments specified by args.'''
        super(DiskmapApp, self).__init__(args)
        # Application variables
        self.__defaultStatus = "Please open a folder to map..."
        self.__mappedDir = ''
        self.__currentFile = ''
        self.__builderThread = None
        
        # Configure the GUIWindow (removed icon dependency)
        self.__window = GUIWindow('Diskmap - Disk Visualization Utility',
                                  640,
                                  360)
        # Configure the Tileframe
        self.__tileframe = TileFrame(self.__window)
        self.__window.setCentralWidget(self.__tileframe)
        self.__window.setMouseTracking(True)
        # Setup remaining GUI elements
        self.__setupMenu()
        self.__setupMouseEvents()
        self.__setupMenuItems()
        self.__window.setStatusBar(self.__defaultStatus)
        # Render the window
        self.__window.show()

    def __setupMenu(self):
        '''Add all the menus used in the application to GUIWindow.'''
        self.__window.addMenu('File')
        self.__window.addMenu('Options')
        self.__window.addMenu('Settings')
        self.__window.addMenu('Help')

    def __setupMouseEvents(self):
        '''Bind event functions for mouse movement, mouse click and mouse
        release events to GUIWindow.'''
        moveEvents = []
        clickEvents = []
        releaseEvents = []
        # Add function to mouse event lists
        moveEvents.append(self.__eventUpdateStatus)
        clickEvents.append(self.__eventPopupMenu)
        # Bind the mouse functions to the mouse events
        self.__window.updateMouseEvents(moveEvents, clickEvents, releaseEvents)

    def __setupMenuItems(self):
        '''Add all the menu items, along with their event functions, used in
        the application to GUIWindow.'''
        # Setup File menu items
        self.__window.addMenuItem('File', 'Map Folder', self.__eventMapFolder)
        self.__window.addMenuSeperator('File')
        self.__window.addMenuItem('File', 'Quit', self.__window.close)
        # Setup Option menu items
        self.__window.addMenuItem('Options',
                                  'Screenshot',
                                  self.__eventScreenshot)
        self.__window.addMenuItem('Options', 'Clear Map', self.__eventClearMap)
        # Setup Settings menu items
        self.__window.addCheckableMenuItem('Settings',
                                           'Gradient',
                                           False,
                                           self.__eventToggleGradient)
        self.__window.addCheckableMenuItem('Settings',
                                           'Borders',
                                           True,
                                           self.__eventToggleBorders)
        # Setup Help menu items
        self.__window.addMenuItem('Help', 'About', self.__eventAbout)

    def __showException(self, exception):
        '''Show a popup message box with the exception that occured.'''
        message = "An unexpected error occured:\n\n {}".format(str(exception))
        QtWidgets.QMessageBox.critical(self.__window,
                                       'Error',
                                       message,
                                       buttons=QtWidgets.QMessageBox.Ok)

    def __eventUpdateStatus(self, event):
        '''Set the status bar text to the file path of the currently mouse
        hovered FileNode from the TileFrame. Set the mouse cursor to a hand
        pointer if a path exists, set the mouse cursor to the standard
        arrow otherwise.'''
        # Nu actualiza statusul dacă se încarcă un folder
        if self.__builderThread and self.__builderThread.isRunning():
            return
            
        path = self.__tileframe.getHoveredNodePath(event)
        if path:
            # Set the cursor to pointing hand cursor
            self.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            # Replace the backslash with forward slash in the file path
            self.__filename = path.replace('\\', '/')
            self.__window.setStatusBar(self.__filename)
        else:
            # Restore cursor back to arrow cursor
            self.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def __eventPopupMenu(self, event):
        '''Create a popup menu iff a visualization map exists and the right
        mouse click event occured. The popup menu contains options to rename,
        move and delete the currently selected file.'''
        # If mouse right click and map is created
        if event.button() == QtCore.Qt.RightButton and \
           self.__tileframe.isMapped():
            menu = QtWidgets.QMenu()
            # Create menu items and bind events to them
            renameFileAction = QtWidgets.QAction('Rename', self)
            moveFileAction = QtWidgets.QAction('Move', self)
            deleteFileAction = QtWidgets.QAction('Delete', self)
            renameFileAction.triggered.connect(self.__eventMenuRenameFile)
            moveFileAction.triggered.connect(self.__eventMenuMoveFile)
            deleteFileAction.triggered.connect(self.__eventMenuDeleteFile)
            # Add actions to menu and create menu
            menu.addAction(renameFileAction)
            menu.addAction(moveFileAction)
            menu.addAction(deleteFileAction)
            menu.exec_(self.__window.mapToGlobal(event.pos()))

    def __getOnlyFilename(self):
        '''Return the name of the file, as a string, from the file's full
        path.'''
        return self.__filename[self.__filename.rfind('/') + 1:]

    def __getOnlyParentFolder(self):
        '''Return the path of the file up to the parent directory, as a string,
        from the file's full path.'''
        return self.__filename[:self.__filename.rfind('/')]

    def __eventMenuRenameFile(self):
        '''Rename a selected file to a new specified name.'''
        message = 'Enter a new name for file: ' + self.__getOnlyFilename()
        text, result = QtWidgets.QInputDialog.getText(self.__window,
                                                      'Message',
                                                      message)
        # If ok was selected and text is no empty
        if result and text:
            # Rename the file and remap the directory
            newFilename = self.__getOnlyParentFolder() + '/' + text
            try:
                os.rename(self.__filename, newFilename)
                self.__eventMapFolderAsync(self.__mappedDir)
            except OSError as error:
                # Exception raised, display message and terminate
                self.__showException(error)

    def __eventMenuMoveFile(self):
        '''Move a selected file to a new specified folder.'''
        flags = QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.\
            DontUseNativeDialog
        folder = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                            'Select a folder:',
                                                            'C:\\', flags)
        # If a folder was selected
        if folder:
            # Move the file to the new destination and remap the directory
            newFileDestination = folder + '/' + self.__getOnlyFilename()
            try:
                os.rename(self.__filename, newFileDestination)
                self.__eventMapFolderAsync(self.__mappedDir)
            except OSError as error:
                # Exception raised, display message and terminate
                self.__showException(error)

    def __eventMenuDeleteFile(self):
        '''Delete a selected file.'''
        message = 'Are you sure you want to delete ' + \
            self.__getOnlyFilename() + '?'
        result = QtWidgets.QMessageBox.question(self.__window,
                                                'Message',
                                                message,
                                                QtWidgets.QMessageBox.Yes,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            try:
                # Delete the file and remap the directory
                os.remove(self.__filename)
                self.__eventMapFolderAsync(self.__mappedDir)
            except OSError as error:
                # Exception raised, display message and terminate
                self.__showException(error)

    def __eventToggleBorders(self):
        '''Toggle rendering borders in the TileFrame.'''
        self.__tileframe.toggleBorders()

    def __eventToggleGradient(self):
        '''Toggle rendering gradients in the TileFrame.'''
        self.__tileframe.toggleGradient()

    def __eventScreenshot(self):
        '''Prompt the user to save a screenshot of the visualization map and
        save the screenshot as a .PNG file.'''
        # If a map is created
        if self.__tileframe.isMapped():
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.__window,
                'Save Screenshot',
                '',
                'Images (*.png)',
                options=QtWidgets.QFileDialog.DontUseNativeDialog)
            if fname:
                if not fname.endswith('.png'):
                    fname += '.png'
                self.__tileframe.screenshot(fname)

    def __onProgressUpdate(self, value):
        '''Callback pentru actualizarea progress bar-ului.'''
        self.__window.updateProgressBar(value)

    def __onStatusUpdate(self, status):
        '''Callback pentru actualizarea statusului.'''
        self.__window.setStatusBar(status)

    def __onBuildComplete(self, treemap):
        '''Callback pentru finalizarea construirii treemap-ului.'''
        self.__window.hideProgressBar()
        
        if treemap and treemap.getRoot():
            self.__tileframe.setTreemap(treemap)
            self.__window.setStatusBar("")
        else:
            self.__window.setStatusBar("Failed to build treemap")
        
        # Curăță thread-ul
        if self.__builderThread:
            self.__builderThread.deleteLater()
            self.__builderThread = None

    def __eventMapFolderAsync(self, folder):
        '''Construiește treemap-ul asincron cu progress bar.'''
        # Dacă mai există un thread în execuție, îl oprim
        if self.__builderThread and self.__builderThread.isRunning():
            self.__builderThread.terminate()
            self.__builderThread.wait()
        
        # Curăță map-ul anterior
        self.__tileframe.clearMap()
        
        # Reset checkable menu items
        self.__window.setCheckedMenuItem('Gradient', False)
        self.__window.setCheckedMenuItem('Borders', True)
        
        # Afișează progress bar-ul
        self.__window.showProgressBar()
        
        # Creează și pornește thread-ul
        self.__builderThread = TreemapBuilderThread(folder)
        self.__builderThread.progress.connect(self.__onProgressUpdate)
        self.__builderThread.status_update.connect(self.__onStatusUpdate)
        self.__builderThread.finished_build.connect(self.__onBuildComplete)
        self.__builderThread.start()

    def __eventMapFolder(self):
        '''Prompt the user to select a folder to use for creating the
        visualization map. Build the visualization if the user has selected a
        valid folder.'''
        flags = QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.\
            DontUseNativeDialog
        folder = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                            'Select a folder:',
                                                            'C:\\', flags)
        # If a folder was selected
        if folder:
            # Store the mapped folder
            self.__mappedDir = folder
            # Construiește treemap-ul asincron
            self.__eventMapFolderAsync(folder)

    def __eventClearMap(self):
        '''Prompt the user to clear the visualization map. Clear the map, reset
        the checkable menu items and set the default status text iff the user
        confirmed Yes to the message prompt.'''
        # If a map is created
        if self.__tileframe.isMapped():
            message = 'Are you sure you want to clear the visualization map?'
            result = QtWidgets.QMessageBox.question(self.__window,
                                                    'Message',
                                                    message,
                                                    QtWidgets.QMessageBox.Yes,
                                                    QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.Yes:
                # Oprește thread-ul dacă rulează
                if self.__builderThread and self.__builderThread.isRunning():
                    self.__builderThread.terminate()
                    self.__builderThread.wait()
                
                # Reset checkable menu items
                self.__window.setCheckedMenuItem('Gradient', False)
                self.__window.setCheckedMenuItem('Borders', True)
                self.__tileframe.clearMap()
                self.__window.hideProgressBar()
                self.__window.setStatusBar(self.__defaultStatus)

    def __eventAbout(self):
        '''Display an information dialog about the program languages and tools
        used to create this application and the name of the developer.'''
        message = 'Disk Space Visualization Utility\n\nPython 3, PyQt 5\n' + \
            '\nCreated by Salinder Sidhu\nProgress Bar Enhancement Added'
        # Render the message box
        QtWidgets.QMessageBox.information(self.__window,
                                          'About',
                                          message,
                                          buttons=QtWidgets.QMessageBox.Ok)


if __name__ == '__main__':
    # Pass command line arguments into application
    myApp = DiskmapApp(sys.argv)
    sys.exit(myApp.exec_())