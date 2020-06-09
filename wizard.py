import os
import sys
from pathlib import Path
from config import paths_config
from logging import log_info, log_success, log, log_warning, log_error


class WizardStep:
  name = "GENERIC_NAME"

  def execute(self):
    raise NotImplementedError()

  def abort(self):
    sys.exit(0)

class EnvFileExistenceStep(WizardStep):
  name = "Configuration with .env file"

  def execute(self):
    env_file_exists = Path(os.path.join(os.getcwd(), ".env"))

    log("Checking if .env file exists...")

    if env_file_exists:
      log_success(f"Success!")
    else:
      log_error("You should have .env file in your project! Please create it with .env.dist file as example")
      self.abort()


class ConfigurePathsStep(WizardStep):
  name = "Paths configuration"

  def execute(self):
    env_file_exists = Path(os.path.join(os.getcwd(), ".env"))

    if env_file_exists:
      log("Your project should have configured paths to work properly. Going to check it now...")

      log("Checking if paths configured...")

      try:
        paths_config.stop_execution_if_paths_not_configured()
      except Exception as e:
        log_warning("Path are not configured. Please check error below:")
        log_error(e)
        self.abort()

      try:
        paths_config.stop_execution_if_paths_not_accessible()
      except Exception as e:
        log_warning("Some paths are not accessible. Please check error below:")
        log_error(e)
        self.abort()

      log_success("Paths are accessible! ")
      log_success("Congratulations, everything seems to be ok with your paths.")
    else:
      log_error(".env file does not exist!")


class DatasetsExistenceStep(WizardStep):
  name = "Check for datasets existence"

  def execute(self):
    log("Checking if your datasets paths are ok... Meaning you actually downloaded them.")
    try:
      paths_config.stop_execution_if_datasets_not_downloaded()
    except Exception as e:
      log_warning("It seems something not right with your datasets path.... See more info below: ")
      log_error(e)
      self.info_about_downloading_datasets()

  def info_about_downloading_datasets(self):
    log_info("***************************************")
    log_info("*** MANUAL FOR DOWNLOADING DATASETS ***")
    log_info("***************************************")
    log_info("If you did not yet download datasets, please use special script created for this")
    log_info("Execute this in your console:")
    log_warning("*** WARNING ***: this will be long running script, so it is advised to start it in tmux session so it would not depent on your terminal session")
    log_info(">>> python downloader.py")
    log_info("After you download datasets, please restart wizard")
    self.abort()

class TrainingStep(WizardStep):
  name = "Actual model training step"

steps = [
  EnvFileExistenceStep(),
  ConfigurePathsStep(),
  DatasetsExistenceStep()
]

i = 1

log_success("**************************")
log_success("*** Welcome to WIZARD! ***")
log_success("**************************")

log_success(
  "I will try to make your journey to train and use ML model for mobile as easy and pleasant as possible"
)

for step in steps:
  log("")
  log_info(f"*** WIZARD STEP {i}: {step.name} ***")

  step.execute()

  i += 1