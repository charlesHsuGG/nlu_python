import pip

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
   "SQLAlchemy",
   "PyYAML"
]

packages = [package.project_name for package in pip.get_installed_distributions()]

for requirment in requirments:  
    if requirment not in packages:
        if requirment is "mitie":
            pip.main(['install', "git+https://github.com/mit-nlp/MITIE.git"])
        else:
            pip.main(['install', requirment])
    else:
        print("already installed "+requirment)