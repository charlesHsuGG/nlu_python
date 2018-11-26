import pip
from pip._internal import main
import pkg_resources

requirments = [
   "gevent",
   "klein",
   "boto3",
   "typing",
   "future",
   "six",
   "jsonschema",
   "matplotlib",
   "requests",
   "tqdm",
   "numpy",
   "simplejson",
   "jieba",
   "scikit-learn",
   "scipy",
   "mitie",
   "spacy",
   "Flask",
   "mysqlclient",
   "flask_sqlalchemy",
   "PyYAML"
]

packages = [package.project_name for package in pkg_resources.working_set]

for requirment in requirments:  
    if requirment not in packages:
        if requirment is "mitie":
            main(['install', "git+https://github.com/mit-nlp/MITIE.git"])
        else:
            main(['install', requirment])
    else:
        print("already installed "+requirment)