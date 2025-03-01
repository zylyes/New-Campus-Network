import win32event
import win32api
import winerror
import logging

class AppMutex:
    def __init__(self, name="Global\\CampusNetLoginApp"):
        self.mutex_name = name
        self.mutex = None
        self.acquired = False

    def acquire(self):
        try:
            self.mutex = win32event.CreateMutex(None, True, self.mutex_name)
            last_error = win32api.GetLastError()
            
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                logging.warning("Mutex already exists, application already running")
                return False
            self.acquired = True
            logging.info("Mutex acquired successfully")
            return True
        except Exception as e:
            logging.error(f"Mutex acquisition failed: {str(e)}")
            return False

    def release(self):
        if self.mutex and self.acquired:
            try:
                win32event.ReleaseMutex(self.mutex)
                win32api.CloseHandle(self.mutex)
                self.acquired = False
                logging.info("Mutex released successfully")
            except Exception as e:
                logging.error(f"Mutex release failed: {str(e)}")