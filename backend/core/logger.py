import logging
import os
from logging.handlers import RotatingFileHandler
import json

# Cria logger singleton
logger = logging.getLogger("griô")

# Evita adicionar handlers múltiplas vezes
if not logger.handlers:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level))

    # Handler para arquivo (JSON estruturado)
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formato JSON estruturado
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                "timestamp": record.created,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info:
                log_obj["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_obj)
    
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Handler para console (desenvolvimento)
    if os.getenv("ENV", "development") == "development":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter(
                '[%(levelname)s] %(name)s: %(message)s'
            )
        )
        logger.addHandler(console_handler)
