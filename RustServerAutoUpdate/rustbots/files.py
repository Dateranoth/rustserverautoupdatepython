import os, errno, shutil, logging, logging.handlers, sys, traceback, glob
from datetime import datetime, timedelta, timezone
class SetupLogging:
    def __init__(self, logPath, logFile, logLevel,  rotateBackups = 10, rotateWhen = 'midnight', rotateInterval = 1):
        """LogBot sets up logging for rustserverautoupdate.
        logPath = Path to Log File Example: /home/rustserver/logs
        logFile = Name of Log File Example: rustserverautoupdate.log
        logLevel = Minimum Level to write to file. Integer: NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, and CRITICAL=50
        rotatBackups, rotateWhen, rotateInterval correspond to logging.handlers.TimedRotatingFileHandler when, interval, backupCount"""
 
        # Get the root logger and set the level to NOTSET (0)
        # This is so other loggers inherit properly.
        # consoleHandler and fileHandler can then be set independently
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        #Check if any handlers are already configured at root level. If so, remove them. (This is obviously intended to be the master logging setup)
        for x in range(0, len(logger.handlers), 1):
            if len(logger.handlers) > 0:
                logger.removeHandler(logger.handlers[0])
         
        # Create a console handler, set the level to DEBUG, and format without timestamp
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(logging.Formatter(fmt='[%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z'))  

        # Create a file handler to write to file and Rotate on schedule, set the level to logLevel, and format with timestamp
        fileHandler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(logPath, logFile), when = rotateWhen, interval = rotateInterval, backupCount = rotateBackups, encoding='utf-8')
        fileHandler.setLevel(logLevel)
        fileHandler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(levelname)s] [%(name)s] [%(message)s]', datefmt='%Y-%m-%d %H:%M:%S%z'))
        
        # Add the Handlers to the logger
        logger.addHandler(consoleHandler)
        logger.addHandler(fileHandler)

        # Create named logger for SetupLogging to use.
        self.logger = logging.getLogger(__name__)
    
    def change_level(self, level, console = False):
        """Update the log Level for the base Log Handler.
        Alternatively update the root console log level.
        Must be string NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL or integer
        Returns current level after updating or -1 for failure
        """
        logger = logging.getLogger()
        newLevel = level
        if isinstance(level, str):
            loggingLevels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
            newLevel = loggingLevels.get(level.upper().strip(), level)
        if isinstance(newLevel, int):
            if console and len(logger.handlers) >= 1 and logger.handlers[0].level != newLevel:
                logger.handlers[0].setLevel(newLevel)
                self.logger.info("Console Log Level Changed to: " + str(logger.handlers[0].level))
                return logger.handlers[0].level
            elif len(logger.handlers) >= 2 and logger.handlers[1].level != newLevel:
                logger.handlers[1].setLevel(newLevel)
                self.logger.info("File Log Level Changed to: " + str(logger.handlers[1].level ))
                return logger.handlers[1].level
            else:
                return newLevel
        else:
            self.logger.error('Incorrect Log Level Specified. Must be string NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL or integer', stack_info=False)
            return -1

class ManageFiles:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def backup_file(self, filePath, fileName, quantity = 10, extension = ".bak"):
        """Creates backup of filePath/fileName into same directoy as filePath/fileName-YYYY-MM-DD-HH.MM.SS-UTCOFFSET.extension
        NOTE: This does a wildcard search of filePath + fileName + * + extension to find and delete
        oldest file after quantity is exceeded. Logs warning if source file not found. Raises FileNotFoundError if backup cannot be found after copy.
        filePath = Path to file to backup.
        fileName = Name of file to backup.
        quantity = Number of backups to keep. Oldest file deleted when quantity exceeded.
        extension = what to append to end of file.        
        """

        #Create the source,  backup, and old backup paths. Write them out to debug.
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN)
        timeStamp =  tm.strftime("-%Y-%m-%d_%H.%M.%S%z")
        wildcard = "*" 
        sourceFilePath = os.path.join(filePath, fileName)
        backupFilePath = os.path.join(filePath, fileName + timeStamp + extension)
        oldFileSearchPath = os.path.join(filePath, fileName + wildcard + extension)
        self.logger.debug("Source: " + sourceFilePath + " Dest: " + backupFilePath + " OldBackups: " + oldFileSearchPath)

        #Check that the source exists. If not, log the warning and return.
        if not os.path.exists(sourceFilePath):
            self.logger.warning("Cannot Backup. File Not Found: " + sourceFilePath)
            return

        #Check for old backups. If more than set quantity, try to delete the oldest.
        oldBackupFiles = sorted(glob.glob(oldFileSearchPath))
        if quantity <= 0: quantity = 1
        if len(oldBackupFiles) >= quantity:
            #Delete the oldest file found. If unable to delete, log the exception.
            #Originally allowed exception to be thrown, but deleting old backups is not critical.
            try:
                os.remove(oldBackupFiles[0])
                self.logger.info("Removed Oldest Backup File: " + oldBackupFiles[0])
            except:
                self.logger.exception("Failed to Remove Oldest Backup File " + oldBackupFiles[0])

        #Copy source to backup. If this fails we want an exception to be thrown as creating the backup is important.
        shutil.copy2(sourceFilePath, backupFilePath)
        if os.path.exists(backupFilePath):
            self.logger.info("Created Backup File: " + backupFilePath)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), backupFilePath)