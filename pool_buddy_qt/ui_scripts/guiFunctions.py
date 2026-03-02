class guiFunctions:
    def openWindow(mainWindow, window, closeCurrent):
        if mainWindow.w is None:
            mainWindow.w = window
            mainWindow.w.show()
            if closeCurrent:
                mainWindow.close()