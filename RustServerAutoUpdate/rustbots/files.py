import os, shutil, logging, logging.handlers, sys, traceback
class SetupLogging:
    def __init__(self, logPath, logFile, logLevel,  rotateBackups = 10, rotateWhen = 'midnight', rotateInterval = 1):
        """LogBot sets up logging for rustserverautoupdate.
        logPath = Path to Log File Example: /home/rustserver/logs
        logFile = Name of Log File Example: rustserverautoupdate.log
        logLevel = Minimum Level to write to file. Integer: NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, and CRITICAL=50
        rotatBackups, rotateWhen, rotateInterval correspond to logging.handlers.TimedRotatingFileHandler when, interval, backupCount"""

        #One Format for console logging and one for file logging.
        consoleFormat = '[%(levelname)s] [%(name)s]: %(message)s'
        fileFormat = '[%(asctime)s][%(levelname)s] [%(name)s] [%(message)s]'
 
        # Configure the Basic Logging. This sets DEBUG output to console. Formats date, but isn't currenlty used in console.
        logging.basicConfig(level=logging.DEBUG, format=consoleFormat, datefmt='%Y-%m-%d %H:%M:%S%z')
        logger = logging.getLogger()

        # Create a file handler to write to file and Rotate nightly. 
        # Set the log level on the handler.
        # Format the date string and set the Formatter on the handler.
        # Add the handler to the logger.
        handler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(logPath, logFile), when = rotateWhen, interval = rotateInterval, backupCount = rotateBackups, encoding='utf-8')
        handler.setLevel(logLevel)
        handler.setFormatter(logging.Formatter(fmt=fileFormat, datefmt='%Y-%m-%d %H:%M:%S%z'))        
        logger.addHandler(handler)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Logging Setup Complete")

class ManageFiles:    
    def backup_file(self, filePath, fileName, quantity = 10, extension = ".bak"):
        """Creates backup of filePath/fileName into same directoy as filePath/fileName-YYYY-MM-DD-HH.MM.SS-UTCOFFSET.extension
        NOTE: This does a wildcard search of filePath + fileName + * + extension to find and delete
        oldest file after quantity is exceeded. Returns True if File copied successfully.
        filePath = Path to file to backup.
        fileName = Name of file to backup.
        quantity = Number of backups to keep. Oldest file deleted when quantity exceeded.
        extension = what to append to end of file.
        """
        
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN)
        timeStamp =  tm.strftime("-%Y-%m-%d_%H.%M.%S%z")
        wildcard = "*"
        sourceFilePath = os.path.join(filePath, fileName)
        backupFilePath = os.path.join(filePath, fileName + timeStamp + extension)
        oldFileSearchPath = os.path.join(filePath, fileName + wildcard + extension)
        self.logger.debug("Source: " + sourceFilePath + " Dest: " + backupFilePath + " OldBackups: " + oldFileSearchPath)
        oldBackupFiles = sorted(glob.glob(oldFileSearchPath))
        if quantity <= 0:
            quantity = 1
        if len(oldBackupFiles) >= quantity:
            remove(oldBackupFiles[0])
            self.logger.info("Removed Backup File: " + oldBackupFiles[0])
        shutil.copy2(sourceFilePath, backupFilePath)
        if os.path.exists(backupFilePath):
            return True
        else:
            return False